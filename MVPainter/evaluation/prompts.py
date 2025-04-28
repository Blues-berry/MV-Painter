class Prompts:
    def __init__(self):
        self.four_views_prompt = '''
        Our task here is the compare two textured 3D objects, both textured from the same 3d shape and reference image.
        We want to decide which one is better according to the provided criteria.

        # Instruction
        You will see an image containing renderings of these two 3D objects. And the second image is the reference image.

        The left part of the image contains four view renderings of 3D object 1, and the right part contains 4 view renderings for 3D object 2.

        We would like to compare these two 3D objects from the following aspects:

        1. 3D Shape-Texture Alignment. This evaluates how well the texture corresponds to the 3D geometry. Please first describe each of the two models, and then evaluate how well the texture correspondes ALL the semantically meaningful parts of the geometry.

        2. Low-Level Texture Quality. Focus on LOCAL parts of the RGB images: whose texture is sharper, more realistic, with high resolution, and with more details? Remember that the local texture quality could be high even if the shape-texture alignment is weak, this is independently evaluated.

        3. Texture-Reference Alignment. This examines how well the texture adheres to the reference image. Which one more closely matches the reference image in both appearance and semantics?

        Take a really close look at each of the images for these two 3D objects before providing your answer.

        When evaluating these aspects, focus on one of them at a time.

        Try to make independent decision between these criteria.

        # Output format
        To provide an answer, please provide a short analysis for each of the abovementioned evaluation criteria.
        The analysis should be very concise and accurate.

        For each of the criteria, you need to make a decision using these three options:
        1. Left (object 1) is better;
        2. Right (object 2) is better;
        3. Cannot decide.
        IMPORTANT: PLEASE USE THE THIRD OPTION SPARSELY.

        And then, in the last row, summarize your final decision by "<option for critera 1> <option for criteria 2> <option for critera 3>".

        An example output looks like follows:
        "
        Analysis:
        1. Text prompt & 3D Alignment: The left one xxxx; The right one xxxx;
        The left/right one is better or cannot decide

        2. Low-Level Texture Quality. The left one xxxx; The right one xxxx;
        The left/right one is better or cannot decide

        3. Low-Level Geometry. The left one xxxx; The right one xxxx;
        The left/right one is better or cannot decide

        4. Texture-Geometry Coherency. The left one xxxx; The right one xxxx;
        The left/right one is better or cannot decide

        Final answer:
        x x x(e.g., 1 2 2 / 3 3 3 / 2 2 2)
        "
        '''

        self.correct_prompt = '''
        You are evaluating a 3D object comparison based on three metrics with given analysis. For each metric, determine which object is better:

        Output 1 if the Left (Object 1) is better,

        Output 2 if the Right (Object 2) is better,

        Output 3 if you cannot decide.
        Return only a 3-digit string with a space interval(e.g., 2 2 2, 1 1 1, 1 2 2, 3 3 3, etc.) corresponding to the results for the three metrics in order.


        Input Analysis:
        
        '''