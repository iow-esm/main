(background:details_on_fluxes)=
# Details on individial fluxes

This section contains physical details about the fluxes that can be calculated in the flux calculator executable.
All fluxes are calculated positive upward, such that e.g. precipitation is always negative.

## List of variables that determine the fluxes

Fluxes may depend on the following variables:
| code | symbol         | description                                                 | provided by      | unit    |
| ---- | -------------- | ----------------------------------------------------------- | ---------------- | ------- |
| ALBE | $\alpha$       | surface albedo                                              | ocean/land model | 1       |
| AMOI | $a_{moisture}$ | turbulent diffusion coefficient for moisture                | atmos model      | 1       |
| AMOM | $a_{momentum}$ | turbulent diffusion coefficient for momentum                | atmos model      | 1       |
|      | $c_d$          | specific heat capacity of dry air at constant pressure      | 1005.0           | J/kg/K  |
|      | $\Delta H_v$   | latent heat of vaporization                                 | 2.501e6          | J/kg    |
|      | $\Delta H_f$   | latent heat of freezing                                     | 0.334e6          | J/kg    |
|      | $\Delta H_s$   | latent heat of sublimation                                  | 2.835e6          | J/kg    |
| FARE | $f_{area}$     | area fraction of this bottom type (between 0 and 1)         | ocean/land model | 1       |
| FICE | $f_{ice}$      | ice area fraction (between 0 and 1)                         | ocean/land model | 1       |
|      | $g$            | graviational acceleration                                   | 9.81             | m/s     |
| PATM | $p_a$          | pressure at lowest atmospheric level                        | atmos model      | Pa      |
| PSUR | $p_s$          | surface pressure                                            | atmos model      | Pa      |
| QATM | $q_{v,a}$      | specific water vapor content (lowest atmospheric grid cell) | atmos model      | kg/kg   |
|      | $q_{v,s}$      | specific water vapor content (at sea / soil surface)        | aux. variable    | kg/kg   |
|      | $R_d$          | dry air gas constant                                        | 287.05           | J/kg/K  |
|      | $R_v$          | water vapor gas constant                                    | 461.51           | J/kg/K  |
|      | $\sigma$       | Stefan-Boltzmann constant                                   | 5.67e-8          | W m$^{-2}$ K$^{-4}$ |
| TATM | $T_a$          | air temperature (lowest atmospheric grid cell)              | atmos model      | K       |
| TSUR | $T_s$          | surface temperature                                         | ocean/land model | K       |
| UATM | $u_a$          | zonal velocity (lowest atmospheric grid cell)               | atmos model      | m/s     |
|      | $u_{min,evap}$ | minimum velocity for CCLM evaporation calculation           | 0.01             | m/s     |
| VATM | $v_a$          | meridional velocity (lowest atmospheric grid cell)          | atmos model      | m/s     |

## Auxiliary variables for fluxes

### Specific water vapor content (at sea/soil surface)

This auxiliary variable ($q_{v,s}$, in kg/kg) describes the specific water vapor content in the air immediately above the surface, i.e. in the logarithmic boundary layer. 

It is used further in the following routines:
|                 | file                               | routine               | variable                         |
| --------------- | ---------------------------------- | --------------------- | -------------------------------- | 
| flux calculator | `flux_lib/mass/flux_mass_evap.F90` | `flux_mass_evap_cclm` | `specific_vapor_content_surface` |

Here is how it is calculated:

#### COSMO-CLM routine for specific water vapor content at sea/ice surface

|                 |                                                                               |               |
| --------------- | ----------------------------------------------------------------------------- | ------------- |
| **requires**    | $f_{ice}$, $p_s$, $R_d$, $R_v$, $T_s$                                         |               |
| **source**      | COSMO-CLM subroutine `initialize_loop`                                        | (`lmorg.f90`) |
| **references**  | \cite{Lowe1977}, \cite{Murray1967}                                            |               |
| **calculation** | over water / over ice:                                                        |               |
|                 | $\: \alpha = 17.2693882 \, / \, \alpha = 21.8745584$                          | 1             |
|                 | $\: T_2 = 35.86 \, / \, T_2 = 7.66$                                           | K             |
|                 | always:                                                                       |               |
|                 | $T_1 = 273.16$                                                                | K             |
|                 | $p_0 = 610.78$                                                                | Pa            |
|                 | $p_{sat} = p_0 \, \exp \left( \alpha \frac{T_s - T_1}{T_s - T_2} \right)    $ | Pa            |
|                 | $\mathbf{q_{v,s}} = \frac{ \frac{R_d}{R_v} p_{sat}}{p_s - \left(1-\frac{R_d}{R_v}\right) p_{sat}}$ | kg/kg |

## Mass fluxes

### Evaporation/condensation mass flux of water

The surface moisture flux (kg/m$^2$/s) is used further in the following routines:

|                 | file                               | routine                  | variable                         |
| --------------- | ---------------------------------- | ------------------------ | -------------------------------- | 
| COSMO-CLM       | `src_conv_tiedtke.f90`             | `organize_conv_tiedtke`  | `-qvsflx`                        |
| COSMO-CLM       | `src_diagbudget.f90`               | `organize_diagbudget`    | `-qvsflx`                        |
| COSMO-CLM &     | `src_integrals.f90`                | `check_qx_conservation`  | `-qvsflx`                        |
| flux calculator | `flux_heat_latent.f90`             | `flux_heat_latent_water` | `flux_mass_evap`                 |
| flux calculator | `flux_heat_latent.f90`             | `flux_heat_latent_ice`   | `flux_mass_evap`                 |
  
Here is how it is calculated:

#### COSMO-CLM routine for evaporation/condensation mass flux
|                 |                                                                                                |                         |
| --------------- | ---------------------------------------------------------------------------------------------- | ----------------------- |
| **requires**    | $a_{moisture}$, $p_s$, $q_{v,a}$, $q_{v,s}$, $R_d$, $R_v$, $T_s$, $u_a$, $u_{min,evap}$, $v_a$ |                         |
| **source**      | COSMO-CLM subroutine `slow_tendencies`                                                         | (`slow_tendencies.f90`) |
| **calculation** | $\tilde{T} = T_s \left(1 + \left(\frac{R_v}{R_d}-1\right) q_{v,s} \right)$                     | K                       |
|                 | $\mathrm{abs}(\vec{u}) = \sqrt{u_a^2+v_a^2}$                                                   | m/s                     |
|                 | $flux_{air} = a_{moisture} \max(\mathrm{abs}(\vec{u}),u_{min,evap}) \frac{p_s}{R_d \tilde{T}}$ | kg m$^{-2}$ s$^{-1}$    |
|                 | $\mathbf{flux\_mass\_evap} = flux_{air} \cdot (q_{v,s} - q_{v,a})$                             | kg m$^{-2}$ s$^{-1}$    |
| **explanation** | First we calculate the temperature $\tilde{T}$ at which dry air at the surface would show the same energy $p\cdot V$ as the moist air which is there now. | |
|                 | We then calculate a mass flux of air coming into contact with the surface. Evaporation is then calculated assuming that this air adjusts its water vapor content to the one at the surface.  | |
