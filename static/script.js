document.addEventListener('DOMContentLoaded', function() {
    // Handle file upload and read the content
    document.getElementById('fileInput').addEventListener('change', function() {
        var file = this.files[0];
        var reader = new FileReader();

        reader.onload = function(event) {
            var text = event.target.result;
            document.getElementById('originalText').value = text;
        };

        reader.readAsText(file);
    });

    // Handle process button click
    document.getElementById('processBtn').addEventListener('click', function() {
        var originalText = document.getElementById('originalText').value;
        var rangeValue = document.getElementById('summaryRange').value;

        if (!originalText) {
            alert("Please enter some text to summarize.");
            return;
        }

        fetch('/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                'text': originalText,
                'range': rangeValue
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                document.getElementById('summarizedText').value = data.summary;
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    // Handle download button click
    document.getElementById('downloadBtn').addEventListener('click', function() {
        var summarizedText = document.getElementById('summarizedText').value;
        var rangeValue = document.getElementById('summaryRange').value;
        var fileInput = document.getElementById('fileInput');
        var originalFileName = fileInput.files.length > 0 ? fileInput.files[0].name.split('.').slice(0, -1).join('.') : 'summary';

        if (!summarizedText) {
            alert("No summary available to download.");
            return;
        }

        var blob = new Blob([summarizedText], { type: 'text/plain' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = `${originalFileName}_summary_${rangeValue}%.txt`;
        a.click();
        URL.revokeObjectURL(url);
    });
});

function updateRangeLabel(value) {
    document.getElementById('rangeValue').innerText = value + '%';
}