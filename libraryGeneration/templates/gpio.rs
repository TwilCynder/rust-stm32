/**
 *	Rust on STM32 Project by Rouilles en GeraniumTM
 *	Copyright (C) 2024 Université de Toulouse :
 *   - Oussama Felfel - oussama.felfel@univ-tlse3.fr
 *   - François Foltete - francois.foltete@univ-tlse3.fr
 *   - Elana Courtines - elana.courtines@univ-tlse3.fr
 *   - Teo Tinarrage - teo.tinarrage@univ-tlse3.fr
 *   - Zineb Moubarik - zineb.moubarik@univ-tlse3.fr
 *
 *  This library aims to provide the following :
 *   - a rust library generation tool to safely access memory ;
 *   - a support to flash STM32 boards ;
 *   - a task scheduling tool that generates the associated rust code.
 *
 *  The development of this library has done as a Proof of Concept and
 *  is currently only tested for STM32F407-G DISC1 Boards.
 *
 *  It is our hope that using this library to enable development on
 *  other boards will be facilitated.
 *
 *
 *	This program is free software: you can redistribute it and/or modify
 *	it under the terms of the GNU General Public License as published by
 *	the Free Software Foundation, either version 3 of the License, or
 *	(at your option) any later version.
 *
 *	This program is distributed in the hope that it will be useful,
 *	but WITHOUT ANY WARRANTY; without even the implied warranty of
 *	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *	GNU General Public License for more details.
**/

{%- import "gpio_macro.rs" as gpiomacro %}
extern crate core;

use crate::core::ptr::read_volatile;
use crate::core::ptr::write_volatile;
use crate::stm32rustlib::various::*;
{% include "address.rs" %}

/**
 * pin = (GPIO# : char, pin# : u32)
 * mode = HIGH/LOW
 */
#[inline(always)]
pub fn digital_write(pin: (char, u32), mode: u8) {
    match pin.0 {
        {%- for component in components %}
        {{gpiomacro.gen_digital_write_switch_case(component.name[-1])}}
        {%- endfor %}
        _ => (),
    }
}

/**
 * Reads the input of a given pin
 * pin = (GPIO# : char, pin# : u32)
 */
#[inline(always)]
pub fn digital_read(pin: (char, u32)) -> u8 {
    match pin.0 {
        {%- for component in components %}
        {{gpiomacro.gen_digital_read_switch_case(component.name[-1])}}
        {%- endfor %}
        _ => 2,
    }
}
