#!/bin/bash

if [ $# -lt 1 ]; then
	echo "Usage: `basename "$0"` <target-key> [<target-class>]"
	echo "<target-key> is the key that will correspond to your"
	echo "<target-class> (optional) is the class of machine your target belongs to."
	echo "If left out then the <target-key> is taken as the class."
	echo "The target class can also already exist. Then no new machine settings file will be created."
	exit
else
	target=$1
fi	

if [ -z $2 ]; then
    target_class=${target}
else
    target_class=$2
fi

echo ""
echo "#################################################"
echo "# You are adding a new target \"$target\".        "
echo "# This target is from the class \"$target_class\"."
echo "#################################################"
echo ""

echo "#################################################"
echo "# 1. Register new target \"$target\" as an available target  "

for t in `awk '{print $1}' AVAILABLE_TARGETS`; do
    if [ "${target}" == "$t" ]; then
        echo "# Target \"$target\" is already registered! "
        echo "# Please change files by hand if you really want to change them."
        echo "# Abort."
        echo "#################################################"
        echo ""
        exit
    fi
done

echo "${target}" >> AVAILABLE_TARGETS
echo "# done."
echo "#################################################"
echo ""


echo "#################################################"
echo "# 2. Create new build scripts from template      "

# subfolders with components that can be built 
buildables=("components" "tools")

build_template="build_target.template"
start_build_template="start_build_target.template"

echo "# TODOs left for $USER: "
echo "# - go to the following files and adapt them for your target \"${target}\""

for b in ${buildables[@]}; do
    for c in `ls -d ./$b/*`; do

        if [ ! -d $c ]; then
            continue
        fi

        if [ ! -f $c/${build_template} ]; then
            continue
        fi

        cp $c/${build_template} $c/build_${target}.sh
        echo "#   $c/build_${target}.sh"

        if [ ! -f $c/${start_build_template} ]; then
            continue
        fi     

        cp $c/${start_build_template} $c/start_build_${target}.sh
        chmod u+x $c/start_build_${target}.sh
        echo "#   $c/start_build_${target}.sh"   

    done
done

echo "#"
echo "#################################################"
echo ""

echo "#################################################"
echo "# 3. Create new machine settings if necessary    "

new_class=true
# get already available target classes
for m in scripts/run/machine_settings_*.py; do
    # cut out everything after last _ and before the dot
    class=${m##*_}
    class=${class%.*}
    if [ "${target_class}" == "$class" ]; then
        echo "# Target class \"${target_class}\" is existing. No new machine settings file is created."
        new_class=false
        break
    fi
done

machine_settings_template="./scripts/run/machine_settings_target_class.template"
if [ ${new_class} == true ]; then
    echo "# TODOs left for $USER: "
    echo "# - go to the following files and adapt them for your target \"${target}\""
    
    cp ${machine_settings_template} ./scripts/run/machine_settings_${target_class}.py
    echo "#   ./scripts/run/machine_settings_${target_class}.py"  
fi

echo "#"
echo "#################################################"
echo ""


run_script_template="./local_scripts/run_target.template"
echo "#################################################"
echo "# 4. Create new run script    "

echo "# TODOs left for $USER: "
echo "# - go to the following files and adapt them for your target \"${target}\""

cp ${run_script_template} ./local_scripts/run_${target}.sh
chmod u+x ./local_scripts/run_${target}.sh
echo "#   ./local_scripts/run_${target}.sh" 

echo "#"
echo "#################################################"
echo ""


if [ -d "./postprocess" ]; then

    echo "#################################################"
    echo "# 5. Create new module loading scripts for postprocessing    "

    echo "# TODOs left for $USER: "
    echo "# - go to the following files and adapt them for your target \"${target}\""    

    cp ./postprocess/load_modules_target.template ./postprocess/load_modules_${target}.sh
    chmod u+x ./postprocess/load_modules_${target}.sh
    echo "#   ./postprocess/load_modules_${target}.sh"  

    echo "#"
    echo "#################################################"
    echo ""

fi

echo "#################################################"
echo "# Further TODOs for $USER to adapt the setup later on:  "
echo "# - Be sure to select the correct target class in your \"global_settings.py\", i.e. machine=\"${target_class}\""
echo "# - Adapt the jobscript template according to your new target."
echo "#"
echo "#################################################"
echo ""
