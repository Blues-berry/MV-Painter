# Data
We provide blender scripts for rendering the MVPainter training dataset in `data_process`.

1. Prepare `meta.txt` that contains the uid and path of all glb files:
    ```
    {"glb_name": "9b4bf051d9c94edebc8dd92c8e897ad5","glb_path","/path/to/glbs/9b4bf051d9c94edebc8dd92c8e897ad5.glb"}
    {"glb_name": "9717942356204671_f8e8cc02ab4a2a6b","glb_path","/path/to/glbs/9717942356204671_f8e8cc02ab4a2a6b.glb"}
    ```
2. Run blender to render multi-view images
    ```
    cd data_process
    python run_blender.py --hdri_dir /path/to/hdri/maps --path /path/to/your/meta.txt --output_dir /path/to/your/output
    ```
3. Convert exr to png
    ```
    cd data_process
    python depth_exr_to_png.py --root_dir /path/to/your/output  
    ```