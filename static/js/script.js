function processImage(type) {
    const resultDiv = document.getElementById('result');
    const resultText = document.getElementById('resultText');
    const resultImage = document.getElementById('resultImage');
    const originalImage = document.getElementById('originalImage');
    const grayscaleImage = document.getElementById('grayscaleImage');
    const edgeImage = document.getElementById('edgeImage');
    const contouredImage = document.getElementById('contouredImage');
    const croppedImage = document.getElementById('croppedImage');

    let formData = new FormData();
    if (type === 'upload') {
        const fileInput = document.getElementById('imageUpload');
        if (!fileInput.files[0]) {
            alert('Please select an image to upload');
            return;
        }
        formData.append('image', fileInput.files[0]);
    } else {
        const imageSelect = document.getElementById('imageSelect');
        if (!imageSelect.value) {
            alert('Please select an image');
            return;
        }
        formData.append('selected_image', imageSelect.value);
    }

    fetch('/process', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error || 'Server error'); });
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            alert(`Error: ${data.error}`);
            resultDiv.classList.add('hidden');
            return;
        }
        resultText.textContent = `Detected License Plate: ${data.text}`;
        const timestamp = new Date().getTime();
        originalImage.src = `${data.steps.original}?t=${timestamp}`;
        grayscaleImage.src = `${data.steps.grayscale}?t=${timestamp}`;
        edgeImage.src = `${data.steps.edge}?t=${timestamp}`;
        contouredImage.src = `${data.steps.contoured}?t=${timestamp}`;
        croppedImage.src = `${data.steps.cropped}?t=${timestamp}`;
        resultImage.src = `${data.steps.annotated}?t=${timestamp}`;

        console.log('Image paths:', {
            original: originalImage.src,
            grayscale: grayscaleImage.src,
            edge: edgeImage.src,
            contoured: contouredImage.src,
            cropped: croppedImage.src,
            annotated: resultImage.src
        });

        // Show result div
        resultDiv.classList.remove('hidden');

        // Animate steps sequentially
        const steps = document.querySelectorAll('.step');
        steps.forEach((step, index) => {
            setTimeout(() => {
                step.classList.add('visible');
            }, index * 300); // Delay each step by 300ms
        });
    })
    .catch(error => {
        console.error('Fetch error:', error);
        alert(`Error: ${error.message}`);
        resultDiv.classList.add('hidden');
    });
}