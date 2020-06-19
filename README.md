# BMU Balancer

Basic LP that assigns power to assets.


## To Run
1. Create a virtualenv with python 3.8
2. Install requirements `pip install -r requirements.txt`
3. Run `python run.py <INPUT_FILE>`, some example files can be found in tests/data/.


## To Test
1. Create a virtualenv with python 3.8
2. Install requirements `pip install -r requirements_test.txt`
3. Run `pytest`


## Overview

### Objective
Maximise power payment - running cost


### Variable creation criteria

**Availability**: Asset must be available at the time of the boa, if not it is not considered in the problem.
**Minimum Non-Zero Time**: If no instruction already in progress then check that the boa duration is sufficiently
over the MNZT, if it is not then do not create a variable for the asset and thus don't consider it's assignment.
MW related variable creation constraints

**Maximum Export / hr**: upper bound must be less than or equal to the limit
**Maximum Import / hr**: lower bound must be less than or equal to the limit
**Maximum Delivery Volume / Available power**: An asset cannot deliver above its maximum delivery value / available power.

Instruction start variable creation constraints
**Minimum Zero time**: If there is not a instruction already in progress, check that the time since the last instruction
is sufficient. If it isn't the you can give the variable an adjusted_start time as the earliest it can switch on.
**Notice To Deviate From Zero**: If the asset cannot switch on in sufficient time for the boa start, create a candidate
with an adjusted_start for when it can switch on.
Instruction end variable creation constraints

**Maximum Delivery Period**: BOA must be less than the maximum delivery period, including the previous instruction,
if this fails then the end for this candidate could be moved forward.

Given these criteria an instruction candidate is created for each n increment of power that the asset can be turned on by.
If the asset has a single import / export level the value options are just 0 and the single power level.


### Constraints

**BOA request**: The sum of the amount delivered by all assets must be equal to the request (within the delivery period, could be less outside).
**Activation price**: If it is used, an asset must exceed it's activation price.
**One candidate per asset**: Each asset must be assigned to exactly one candidate option


## Next-up
* Expand README
* Add in variable ramp rates
* Collect more-realistic data a tune using this
