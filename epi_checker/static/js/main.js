document.getElementById('upload-btn').addEventListener('click', function() {
    // Show the loading indicator
    document.getElementById('loading-indicator').style.display = 'block';

    // Prepare FormData
    var formData = new FormData();
    var fileInput = document.getElementById('file-input');
    formData.append('file', fileInput.files[0]);

    // Perform the upload
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json()) // Assuming the server sends back JSON
    .then(data => {
        // Hide the loading indicator
        document.getElementById('loading-indicator').style.display = 'none';

        // Show the download link
        var downloadLink = document.getElementById('download-link');
        downloadLink.style.display = 'block';
        downloadLink.href = data.downloadUrl; // The URL should be provided by your server
    })
    .catch(error => {
        console.error('Error:', error);
        // Optionally handle the error
    });
});
