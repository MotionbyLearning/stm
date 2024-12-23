---
title: 'STMTools: Xarray extension for Interferometric SAR data in Space-Time Matrix format'
tags:
  - Python
  - Interferometric
  - Synthetic Aperture Radar
  - InSAR
  - Dask
  - Xarray
authors:
  - name: Ou Ku
    orcid: 0000-0002-5373-5209
    affiliation: 1 
  - name: Fakhereh Alidoost
    orcid: 0000-0001-8407-6472
    affiliation: 1
  - name: Pranav Chandramouli
    orcid: 0000-0002-7896-2969
    affiliation: 1
  - name: Thijs van Lankveld
    orcid: 0009-0001-1147-4813
    affiliation: 1
  - name: Meiert W. Grootes
    orcid: 0000-0002-5733-4795
    affiliation: 1
  - name: Francesco Nattino
    orcid: 0000-0003-3286-0139
    affiliation: 1
  - name: Freek van Leijen
    orcid: 0000-0002-2582-9267
    affiliation: 2
affiliations:
 - name: Netherlands eScience Center, Netherlands
   index: 1
 - name: Delft University of Technology, Netherlands
   index: 2
date: 23 Dec 2024
bibliography: paper.bib
---

## Summary

Interferometry Synthetic Aperture Radar (InSAR) is a crucial technology for monitoring ground surface deformation. It has essential value in various applications, such as civil-infrastructure stability [@chang2014detection; @chang2017railway], hydrocarbons extraction [@fokker2016application; @ZHANG2022102847], etc. To efficiently process and analyze these datasets, researchers has proposed the Space-Time Matrix (STM) format for InSAR datasets [@Bruna2021, @vanLeijen2021], which enanbles the intergration of the contextual information with the InSAR data to reveal the mechanisms driving deformation.  

## Statement of Need

Typiclally, modern time-series InSAR methods is able to provides millions of observation points in a single dataset. However, due the complex and ambiguous nature of InSAR observations, interpretation of these datasets is challenging. [@hanssen2001radar] Under the STM framework, contextual information such as temperature, precipitation, land-use, etc. can be integrated with InSAR data. This can enable a better understanding on the driving mechanisms of the ground deformation, resulting in more reliable and accurate interpretation of the InSAR data. [@Bruna2021, @vanLeijen2021]

To implement the STM format in Python, we developed the `STMTools` package. `STMTools` is developed as an extension of `Xarray`, leveraging `Xarray`'s support for labeled multi-dimensional arrays for the Space-Time concept. `STMTools` provides a set of tools to efficiently connect the InSAR data with various contextual information, such as cadastral data, weather data, etc. The package also utilizes `Dask` for parallel computing, enabling the processing of large-scale InSAR datasets.

## Tutorial

We provide a tutorial as a Jupyter notebook to demonstrate the basic functionalities of `STMTools`:

- [Load InSAR data in STM format](https://tudelftgeodesy.github.io/stmtools/stm_init/)

- [Basic operations with an STM](https://tudelftgeodesy.github.io/stmtools/operations/)

- [Reorder STM in Morton Ordering](https://tudelftgeodesy.github.io/stmtools/order/)


## Acknowledgements

The authors express sincere gratitude to the Dutch Research Council (Nederlandse Organisatie voor Wetenschappelijk Onderzoek, NWO) for their generous funding of the `STMTools` development through the Collaboration in Innovative Technologies (CIT 2021) Call, grant NLESC.CIT.2021.006. Special thanks to SURF for providing valuable computational resources for `STMTools` testing.

## References
