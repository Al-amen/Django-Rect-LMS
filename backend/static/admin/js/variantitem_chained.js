(function($) {
    $(document).ready(function() {
        var courseSelect = $('#id_course');
        var variantSelect = $('#id_variant');

        function loadVariants(courseId) {
            if (!courseId) {
                variantSelect.empty();
                variantSelect.append('<option value="">---------</option>');
                return;
            }

            $.ajax({
                url: window.location.pathname + 'get-variants/',
                data: { 'course_id': courseId },
                success: function(data) {
                    variantSelect.empty();
                    variantSelect.append('<option value="">---------</option>');
                    data.forEach(function(item) {
                        variantSelect.append('<option value="' + item.id + '">' + item.title + '</option>');
                    });
                }
            });
        }

        courseSelect.change(function() {
            loadVariants($(this).val());
        });

        // On page load, if course is selected, load variants
        if (courseSelect.val()) {
            loadVariants(courseSelect.val());
        }
    });
})(django.jQuery);
