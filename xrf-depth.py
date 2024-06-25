# xrf layer thickness calculator by ZH 2024/06/25
# theoretical, needs empirical testing


from xraydb import mu_elam, atomic_density
from math import log


def get_fluorescence_depth_mm(matrix_element:str, fluorescence_energy_ev:int|float, detectable_photon_fraction:float=0.01) -> float:
	"""Returns the max depth of `matrix_element` (element symbol) through which fluorescence at 
	energy `fluorescence_energy_ev` (line energy of interest in ev) will be perceptible to XRF detector, 
	given it is in a matrix of `matrix_element`.\n
	`detectable_photon_fraction` (range 0 -> 1) is the proportion of 
	fluorescence photons to input photons in order to be picked up by the detector. 
	A typical good value for this is 0.01 (1%)"""

	matrix_element_density = atomic_density(matrix_element)
	mass_attenuation_coeff_at_energy = mu_elam(matrix_element, fluorescence_energy_ev)
	depth_in_cm = log(detectable_photon_fraction) / ((-1 * mass_attenuation_coeff_at_energy) * matrix_element_density)
	depth_in_mm = depth_in_cm * 10
	
	return depth_in_mm


def main() -> None:
	matrix_element = input("Matrix Element (symbol): ")
	line_energy_kev = float(input("Fluorescence Line energy of interest (keV): "))
	percentage_of_counts = float(input("Proportion of returning fluorescence counts required for detectability (0 < x <= 1 , suggested: 0.01): "))
	fluorescence_depth_mm = get_fluorescence_depth_mm(matrix_element, (line_energy_kev*1000), detectable_photon_fraction=percentage_of_counts)
	# fluorescence_depth_cm = fluorescence_depth_mm * 10
	# fluorescence_depth_micron = fluorescence_depth_mm / 1000

	print(f"Max depth that fluorescence at {line_energy_kev}keV will be detectable through solid {matrix_element} (with {percentage_of_counts*100:.2f}% returned photons): {fluorescence_depth_mm:.3f}mm")



if __name__ == "__main__":
	main()