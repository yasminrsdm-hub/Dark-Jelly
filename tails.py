import requests
import h5py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import Circle
import os
import io

# --- 1. CONFIGURATION ---

API_KEY = "4ff6dd78476d70518200141e4f2e2268"

SIMULATION = 'TNG100-1'
BASE_URL = f'https://www.tng-project.org/api/{SIMULATION}/'

GALAXIES_TO_TRACK = [
    {"final_snap": 67, "id": 107813},
    {"final_snap": 67, "id": 74123},
    {"final_snap": 72, "id": 96419},
    {"final_snap": 72, "id": 70711},
    {"final_snap": 84, "id": 132263},
    {"final_snap": 99, "id": 108037},
    {"final_snap": 99, "id": 125033},
    {"final_snap": 99, "id": 143888},
    {"final_snap": 91, "id": 124318},
    {"final_snap": 91, "id": 139737},
    {"final_snap": 99, "id": 158854},
    {"final_snap": 91, "id": 141670},
    {"final_snap": 84, "id": 130203},
    {"final_snap": 84, "id": 140404},
    {"final_snap": 78, "id": 124397},
    {"final_snap": 91, "id": 168847},
    {"final_snap": 84, "id": 144300},
    {"final_snap": 78, "id": 148900},
    {"final_snap": 99, "id": 227576},
    {"final_snap": 99, "id": 235696},
    {"final_snap": 99, "id": 281704},
    {"final_snap": 99, "id": 314772},
]


START_SNAP = 67
PLOT_SIZE_CKPC = 60
RESOLUTION_PIXELS = 400
SFR_MIN = 1e-6
SFR_MAX = 1e-1

# --- 2. HELPER FUNCTIONS ---

def get_api_data(url):
    headers = {"api-key": API_KEY}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def get_snapshot_data(snap_num, subhalo_id):
    subhalo_url = f"{BASE_URL}snapshots/{snap_num}/subhalos/{subhalo_id}/"
    subhalo_details = get_api_data(subhalo_url)

    cutout_url = subhalo_details['cutouts'].get('subhalo') or subhalo_details['cutouts']['parent_halo']
    cutout_request = {'gas': 'all', 'stars': 'all'}
    headers = {"api-key": API_KEY}

    response = requests.get(cutout_url, headers=headers, params=cutout_request)
    response.raise_for_status()

    with h5py.File(io.BytesIO(response.content), "r") as f:
        gas_data = {}
        star_data = {}
        if 'PartType0' in f:
            gas_data = {key: f['PartType0'][key][:] for key in f['PartType0'].keys()}
        if 'PartType4' in f:
            star_data = {key: f['PartType4'][key][:] for key in f['PartType4'].keys()}
        header = {key: val for key, val in f['Header'].attrs.items()}

    return subhalo_details, gas_data, star_data, header

def get_surface_density_map(coords, weights, plot_range, pixels, center_pos, box_size):
    dx = coords[:, 0] - center_pos[0]
    dy = coords[:, 1] - center_pos[1]
    dx[dx > box_size/2] -= box_size
    dx[dx < -box_size/2] += box_size
    dy[dy > box_size/2] -= box_size
    dy[dy < -box_size/2] += box_size

    pixel_area_kpc2 = (plot_range / pixels)**2

    hist, _, _ = np.histogram2d(
        dx, dy,
        bins=pixels,
        range=[[-plot_range/2, plot_range/2], [-plot_range/2, plot_range/2]],
        weights=weights
    )
    return hist.T / pixel_area_kpc2

# --- 3. MAIN PROCESSING LOOP ---

output_dir_main = "galaxy_evolution_plots"
os.makedirs(output_dir_main, exist_ok=True)

for g in GALAXIES_TO_TRACK:
    final_snap = g['final_snap']
    final_id = g['id']
    galaxy_output_dir = os.path.join(output_dir_main, f"galaxy_{final_id}_history")
    os.makedirs(galaxy_output_dir, exist_ok=True)

    print(f"\n--- Tracking Galaxy {final_id} from snap {final_snap} back to {START_SNAP} ---")

    current_snap = final_snap
    current_id = final_id

    while current_snap >= START_SNAP and current_id != -1:
        print(f"  Processing Snapshot: {current_snap}, Subhalo ID: {current_id}")
        try:
            subhalo_cat, gas_data, star_data, header = get_snapshot_data(current_snap, current_id)
            redshift = header['Redshift']
            box_size = header['BoxSize']

            # Use correct position fields
            if 'pos_x' in subhalo_cat and 'pos_y' in subhalo_cat and 'pos_z' in subhalo_cat:
                subhalo_pos = np.array([subhalo_cat['pos_x'], subhalo_cat['pos_y'], subhalo_cat['pos_z']])
            elif 'cm_x' in subhalo_cat and 'cm_y' in subhalo_cat and 'cm_z' in subhalo_cat:
                subhalo_pos = np.array([subhalo_cat['cm_x'], subhalo_cat['cm_y'], subhalo_cat['cm_z']])
            else:
                raise KeyError("No position keys found in subhalo_cat")

            # Stellar mass log (use mass_log_msun if available)
            stellar_mass_log = subhalo_cat.get("mass_log_msun", 0.0)

            # Half mass radius of stars
            half_mass_rad_stars = subhalo_cat.get('halfmassrad_stars', 0.0)
            r_dist = 2 * half_mass_rad_stars

            if 'StarFormationRate' not in gas_data or len(gas_data['StarFormationRate']) == 0:
                print("    Warning: No gas with SFR. Skipping plot.")
                current_id = int(subhalo_cat['related']['sublink_progenitor'].split('/')[-2])
                current_snap -= 1
                continue

            sfr_values = gas_data['StarFormationRate']
            sfr_map = get_surface_density_map(gas_data['Coordinates'], sfr_values, PLOT_SIZE_CKPC, RESOLUTION_PIXELS, subhalo_pos, box_size)
            sfr_map[sfr_map <= 0] = 1e-10

            if 'Masses' not in star_data or len(star_data['Masses']) == 0:
                print("    Warning: No star particles found.")
                peak_stellar_density = 0
                stellar_mass_map = np.zeros_like(sfr_map)
            else:
                star_masses = star_data['Masses'] * 1e10 / header['HubbleParam']
                stellar_mass_map = get_surface_density_map(star_data['Coordinates'], star_masses, PLOT_SIZE_CKPC, RESOLUTION_PIXELS, subhalo_pos, box_size)
                peak_stellar_density = np.max(stellar_mass_map)

            contour_levels = [
                0.6 * peak_stellar_density,
                0.7 * peak_stellar_density,
                0.8 * peak_stellar_density
            ] if peak_stellar_density > 0 else []

            fig, ax = plt.subplots(figsize=(6, 6), facecolor='black')
            ax.set_facecolor('black')

            ax.imshow(sfr_map, origin='lower',
                      extent=[-PLOT_SIZE_CKPC/2, PLOT_SIZE_CKPC/2, -PLOT_SIZE_CKPC/2, PLOT_SIZE_CKPC/2],
                      cmap='inferno', norm=LogNorm(vmin=SFR_MIN, vmax=SFR_MAX))

            if contour_levels:
                ax.contour(stellar_mass_map, levels=contour_levels, colors='cyan', linewidths=0.5, alpha=0.6,
                           extent=[-PLOT_SIZE_CKPC/2, PLOT_SIZE_CKPC/2, -PLOT_SIZE_CKPC/2, PLOT_SIZE_CKPC/2])

            ax.add_patch(Circle((0, 0), r_dist, edgecolor='turquoise', facecolor='none', linewidth=1.5, linestyle='--'))

            ax.text(0.05, 0.95, f'TNG50-1\nlog M$_*$ = {stellar_mass_log:.1f}\nz = {redshift:.2f}, ID = {current_id}',
                    transform=ax.transAxes, ha='left', va='top', color='white', fontsize=10)

            ax.plot([-PLOT_SIZE_CKPC/2 + 5, -PLOT_SIZE_CKPC/2 + 15], [-PLOT_SIZE_CKPC/2 + 5, -PLOT_SIZE_CKPC/2 + 5],
                    color='white', linewidth=2)
            ax.text(-PLOT_SIZE_CKPC/2 + 5, -PLOT_SIZE_CKPC/2 + 7, '10 ckpc', color='white', fontsize=9)

            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlim(-PLOT_SIZE_CKPC/2, PLOT_SIZE_CKPC/2)
            ax.set_ylim(-PLOT_SIZE_CKPC/2, PLOT_SIZE_CKPC/2)

            plt.tight_layout()
            output_filename = os.path.join(galaxy_output_dir, f"snap_{current_snap:03d}_id_{current_id}.png")
            plt.savefig(output_filename, dpi=150, facecolor='black')
            plt.close(fig)

            print(f"    -> Saved plot to {output_filename}")

            # Get progenitor ID for next iteration
            prog_url = subhalo_cat['related']['sublink_progenitor']
            if prog_url == "http://www.tng-project.org/api/null":
                break
            current_id = int(prog_url.rstrip('/').split('/')[-1])
            current_snap -= 1

        except requests.exceptions.HTTPError as e:
            print(f"    HTTP ERROR: Subhalo {current_id} at snapshot {current_snap}: {e}")
            break
        except Exception as e:
            print(f"    ERROR: {e}")
            break

    print(f"--- Finished tracking for galaxy ID {final_id} ---")

print("\nAll processing complete.")



