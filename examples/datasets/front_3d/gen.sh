#!/bin/bash

# Define the function to be executed on exit
function on_exit {
  blenderproc run /home/m/ws/BlenderProc?examples/datasets/front_3d/prepare_top_view_data.py
}

# Set the trap to call the function on exit
trap on_exit EXIT

# Your main script code here
echo "Hello, world!"