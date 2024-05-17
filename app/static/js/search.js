$(document).ready(function() {
    $('#searchForm').on('submit', function(event) {
        event.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        var data = form.serialize();
        
        $.ajax({
            type: 'GET',
            url: url,
            data: data,
            dataType: 'json',
            success: function(response) {
                $('#search-results').html(response.html_requests + response.html_recipes + response.html_replies);
            }
        });
    });
});
