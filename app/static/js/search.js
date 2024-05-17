$(document).ready(function() {
    $("#searchForm").submit(function(event) {
        event.preventDefault(); // Prevent the default form submission

        // Get the form data
        var formData = $(this).serialize();

        // Send an AJAX request to the server with the form data
        $.ajax({
            type: "GET",
            url: $(this).attr('action'),
            data: formData,
            dataType: "json", // Expect JSON response from the server
            success: function(response) {
                // Insert the received HTML into the search-results div
                $("#search-results").html('<ul class="list-group">' + response.html + '</ul>');

                // Update the welcome message
                $("#welcomeMessage").text('Search results for "' + response.search_query + '"');

                // Keep the search query and meal type in the form
                $("#search_query").val(response.search_query);
                $("#meal_type").val(response.meal_type);
            },
            error: function(xhr, status, error) {
                console.error("Error:", error); // Log any errors to the console
            }
        });
    });
});
