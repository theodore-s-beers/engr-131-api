from typing import Any

total_points: float = [2.0, 2.0, 2.0, 2.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 3.0, 3.0, 3.0, 3.0, 3.0]

solutions: dict[str, Any] = {
    "q1-1-what-is-scikit-image-used-for": 'Image processing and analysis',
    "q1-2-what-type-of-data-structure-does-scikit-image-use-to-represent-images": 'NumPy arrays',
    "q1-4-what-coordinate-convention-does-scikit-image-use-for-images": 'Matrix-style indexing with (0, 0) at the top-left corner',
    "q1-5-what-does-image-segmentation-do-in-scikit-image": 'It labels pixels in an image to identify objects of interest.',
    "q1-6-how-to-do-edge-detection-in-scikit-image": '`feature.canny`',
    "q3-1-images-in-scikit-image-are-stored-as-numpy-arrays-TF": 'True',
    "q3-2-the-io-submodule-in-scikit-image-is-used-for-reading-and-writing-images-TF": 'True',
    "q3-3-scikit-image-is-designed-specifically-for-3d-image-analysis-TF": 'False',
    "q3-4-the-origin-0-0-in-scikit-image-images-is-located-at-the-bottom-left-corner-TF": 'False',
    "q3-5-scikit-image-color-images-are-represented-as-arrays-with-an-extra-dimension-for-rgb-channels-TF": 'True',
    "q3-6-edge-detection-works-perfectly-for-all-segmentation-problems-TF": 'False',
    "q2-1-which-of-the-following-are-key-functionalities-of-numpy-arrays-in-scikit-image": ['Efficiently storing image data', 'Applying mathematical operations to images', 'Enabling pixel-wise manipulations'],
    "q2-2-which-of-the-following-image-properties-can-be-calculated-using-numpy-arrays-in-scikit-image": ['Image dimensions', 'Intensity range', 'Average brightness'],
    "q2-3-which-of-the-following-functionalities-are-supported-by-scikit-image": ['Loading images from files', 'Applying filters', 'Visualizing images with matplotlib', 'Performing mathematical operations on images'],
    "q2-4-which-of-the-following-submodules-belong-to-scikit-image": ['`io`', '`filters`', '`data`'],
    "q2-5-what-are-challenges-in-image-segmentation": ['Uneven lighting in images', 'Similar intensity levels for objects and background', 'Small gaps in detected edges'],
}
