
# Evaluation
Based on [GPTEval3D](https://github.com/3DTopia/GPTEval3D/tree/main), we designed a human-aligned evaluation method for 3D texturing task. Our evaluation method focuses on three dimension: **alignment with geometry、 alignment with reference image，and texture details quality**.


Here, we provide the code for evaluating different texturing methods in the `MVPainter/evaluation` folder.


1. Render images for evaluation

    Render images for all methods to be evaluated.

    ```
    cd evaluation
    python render_eval.py --textured_glb_dir /path/to/textured/glb/dir --exp_name method1
    ```


2. Paired comparison 

    Combine all methods to be evaluated in pairs and use VLM for pairwise comparison:

    ```
    python eval_pair.py --dir_a eval_temp/method_a --dir_b eval_temp/method_b --output_dir eval_temp/method_a_vs_method_b
    ```

    Since the final answer of VLM will be inconsistent with its analysis, we correct the final answer from the output of VLM:

    ```
    python correct_eval.py --input_dir eval_temp/method_a_vs_b
    ```


    Note: we use the [Qwen2.5-VL-32B-Instruct](https://huggingface.co/Qwen/Qwen2.5-VL-32B-Instruct) model for paried comparison. Please refer to the official instructions for installation environment. 
    
3. Calculate metrics
    Given the pairwise comparison results of all methods to be evaluated, we can calculate their elo scores.


    Frist edit `pair_result_dirs` and `pair_names`in `calculate_metric.py`. To correctly calculate their scores, `pair_names` should correspond to the method names that passed to `pair_result_dirs`.

    Then run following script to get results.
    ```
    python calculate_metric.py
    ```
    




    Note: we use [EloPy](https://github.com/HankSheehan/EloPy) to claculate elo ranking scores of all evaluated methods. Please install it from source.

