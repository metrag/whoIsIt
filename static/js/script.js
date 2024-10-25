document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.querySelector('.upload-area');
    const recognizeButton = document.querySelector('.recognize-button');
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.style.display = 'none';
    uploadArea.appendChild(fileInput);

    let selectedImage = null;

    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                selectedImage = event.target.result;
                displayPreview(selectedImage);
                recognizeButton.disabled = false;
            }
            reader.readAsDataURL(file);
        }
    });

    function displayPreview(imageSrc) {
        const existingImageContainer = uploadArea.querySelector('.image-container');
        if (existingImageContainer) {
            existingImageContainer.remove();
        }

        const imageContainer = document.createElement('div');
        imageContainer.classList.add('image-container');

        const img = document.createElement('img');
        img.src = imageSrc;
        img.style.maxWidth = '100%';
        img.style.maxHeight = '100%';
        img.style.objectFit = 'contain';

        imageContainer.appendChild(img);
        uploadArea.appendChild(imageContainer);

        uploadArea.classList.add('has-image');
    }

    function sendFileToServer(base64Image) {
        fetch('/upload-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: base64Image })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Успех:', data);
            displayResults(data.results);
        })
        .catch((error) => {
            console.error('Ошибка:', error);
        });
    }

    function displayResults(results) {
        const resultContainer = document.querySelector('.result-container');
        resultContainer.textContent = results; // или добавьте HTML-код с результатами
        resultContainer.style.display = 'block'; // Показываем контейнер с результатами
        
        if (!resultContainer) {
            const newResultContainer = document.createElement('div');
            newResultContainer.classList.add('result-container');
            document.querySelector('.content').appendChild(newResultContainer);
        }
        
        const resultList = document.createElement('ul');
        results.forEach(result => {
            const listItem = document.createElement('li');
            listItem.textContent = `${result.class}: ${result.probability.toFixed(2)}%`;
            resultList.appendChild(listItem);
        });

        const existingResultContainer = document.querySelector('.result-container');
        existingResultContainer.innerHTML = '';
        existingResultContainer.appendChild(resultList);
    }

    recognizeButton.addEventListener('click', function() {
        if (selectedImage) {
            sendFileToServer(selectedImage);
        } else {
            alert('Пожалуйста, сначала выберите изображение');
        }
    });

    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });

    uploadArea.style.cursor = 'pointer';
    recognizeButton.disabled = true;
});