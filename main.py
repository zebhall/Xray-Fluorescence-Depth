import flet as ft
import pandas as pd
from element_string_lists import (
    element_z_to_name,
    element_z_to_symbol,
    element_z_to_symbol_z,
    element_symbol_to_name,
)
from xrf_depth import get_fluorescence_depth_mm


def get_atomic_data_from_csv(file_path: str) -> pd.DataFrame:
    atomic_df = pd.read_csv(file_path, index_col="Atomic#")
    print(atomic_df)
    return atomic_df


def get_element_line_energy_kev(atomic_df: pd.DataFrame, z: int, line: str) -> float:
    """`fluorescence_line` must be one of `["Ka1", "Ka2", "Kb1", "Kb2", "Kb3", "La1", "La2", "Lb1", "Lb2", "Lb3", "Lb4", "Lg1", "Lg2", "Lg3", "Ll"]`"""
    fluo_energy = atomic_df.loc[z, line]
    # print(f"energy of {element_z_to_name(z)} {line} = {fluo_energy}keV")
    return fluo_energy


def get_available_line_energies(
    atomic_df: pd.DataFrame, z: int
) -> list[tuple[str, float]]:
    """
    takes the 'atomic' dataframe and returns a list of tuples.
    Each tuple has two items: line name as str e.g. `"Ka1"`, and energy in keV as float e.g. `1.73998`"

    Args:
    - atomic_df (pd.DataFrame): The input pandas dataframe for atomic data (imported from Atomic.csv by calling `get_atomic_data_from_csv`)\n
    - z (int) : The atomic number you want lines for
    Returns:
    list of tuples: eg. `[("Ka1", 1.73998), ("Ka2", 1.73938) ... ]`
    """
    line_names = [
        "Ka1",
        "Ka2",
        "Kb1",
        "Kb2",
        "Kb3",
        "La1",
        "La2",
        "Lb1",
        "Lb2",
        "Lb3",
        "Lb4",
        "Lg1",
        "Lg2",
        "Lg3",
        "Ll",
    ]
    line_energy_tuples_list: list[tuple[str, float]] = []
    for line in line_names:
        energy = get_element_line_energy_kev(atomic_df, z, line)
        if energy != 0:
            line_energy_tuples_list.append((line, energy))
    return line_energy_tuples_list


def df_to_z_sym_name_tuples(atomic_df: pd.DataFrame) -> list[tuple[int, str, str]]:
    """
    takes the 'atomic' dataframe and returns a list of tuples.
    Each tuple has three items: row index aka "Atomic#",
    the str value of the "Symbol" column, and the str value of the "ElementName" column.

    Args:
    atomic_df (pd.DataFrame): The input pandas dataframe for atomic data (imported from Atomic.csv by calling `get_atomic_data_from_csv`)

    Returns:
    list of tuples: eg. `[(1, "H", "Hydrogen"), (2, "He", "Helium") ... ]`
    """
    z_sym_name_tuples_list: list[tuple[int, str, str]] = []
    for index, row in atomic_df.iterrows():
        z_sym_name_tuples_list.append((index, row["Symbol"], row["ElementName"]))
    return z_sym_name_tuples_list


def main(page: ft.Page):
    # INITAL VARS AND SETTINGS
    page.title = "X-Ray Fluorescence Depth Calc"
    app_width = 500
    app_height = 500

    # get atomic data
    atomic_df = get_atomic_data_from_csv("Atomic.csv")
    get_element_line_energy_kev(atomic_df, z=26, line="Ka1")

    def dropdown_elementofinterest_changed(e) -> None:
        dropdown_lineofinterest.options.clear()
        for _line, _energy in get_available_line_energies(
            atomic_df, int(dropdown_elementofinterest.value)
        ):
            dropdown_lineofinterest.options.append(
                ft.dropdown.Option(
                    key=_energy,
                    text=f"{element_z_to_symbol(int(dropdown_elementofinterest.value))} {_line}\t({_energy} keV)",
                )
            )
        page.update()

    def dropdown_lineofinterest_changed(e) -> None:
        matrix_ele_sym = element_z_to_symbol(int(dropdown_matrixelement.value))
        eoi_sym = element_z_to_symbol(int(dropdown_elementofinterest.value))
        line_energy_kev = float(dropdown_lineofinterest.value)
        line_energy_ev = line_energy_kev * 1000
        pctg_counts_detectable = 0.01
        result = get_fluorescence_depth_mm(
            matrix_element=matrix_ele_sym,
            fluorescence_energy_ev=line_energy_ev,
            detectable_photon_fraction=pctg_counts_detectable,
        )
        print(result)
        text_spiel.value = f"Max depth that {eoi_sym} fluorescence at {line_energy_kev}keV will be detectable through solid {matrix_ele_sym} (with {pctg_counts_detectable*100:.2f}% returned photons):"
        text_result.value = f"{result:.3f}mm"
        page.update()

    # create element dropdown controls and add options
    dropdown_elementofinterest = ft.Dropdown(
        label="Element of Interest",
        on_change=dropdown_elementofinterest_changed,
        helper_text="The Element you're trying to detect",
    )
    dropdown_matrixelement = ft.Dropdown(
        label="Matrix Element",
        helper_text="The Element covering the Element-of-interest",
    )
    dropdown_lineofinterest = ft.Dropdown(
        label="Spectral Line",
        helper_text="Which line are you using to analyse your element of interest?",
        on_change=dropdown_lineofinterest_changed,
    )
    for ele_z, ele_sym, ele_name in df_to_z_sym_name_tuples(atomic_df):
        # dropdown.value method will return key, which is handy for just getting z val instead of whole string
        dropdown_elementofinterest.options.append(
            ft.dropdown.Option(key=ele_z, text=f"{ele_z}\t{ele_sym}\t{ele_name}")
        )
        dropdown_matrixelement.options.append(
            ft.dropdown.Option(key=ele_z, text=f"{ele_z}\t{ele_sym}\t{ele_name}")
        )

    # create result control
    text_spiel = ft.Text("")
    text_result = ft.Text("", size=16, weight=ft.FontWeight.BOLD)

    # BUTTONS

    # LHS and RHS of main container

    # column_RHS = ft.Column(
    # 	controls=[ft.Text(value="test")],
    # )

    # main container containing all contents of app
    container_root = ft.Container(
        content=ft.Column(
            controls=[
                dropdown_elementofinterest,
                dropdown_matrixelement,
                dropdown_lineofinterest,
                text_spiel,
                text_result,
            ]
        ),
        padding=ft.padding.all(30),
        margin=ft.margin.all(5),
        width=app_width,
        height=app_height,
        border_radius=10,
    )

    page.add(container_root)


if __name__ == "__main__":
    ft.app(main)
