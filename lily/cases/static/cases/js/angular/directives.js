var caseDirectives = angular.module('CaseDirectives', []);

caseDirectives.directive("updateCaseExpireDate", ['$rootScope', function($rootScope) {
    return {
        restrict: "A",
        link: function(scope, element, attrs) {

            var select = $('#id_priority');
            var daysToAdd = [5, 3, 1, 0];

            select.on('change', function(event) {
                var priority = parseInt(select.val());
                if(select.val() == NaN){
                    priority = 3;
                }
                var due = addBusinessDays(new Date(), daysToAdd[priority]);
                var month = due.getMonth() + 1;
                if(month < 10){
                    month = "0" + month;
                }
                var expires = due.getDate() + '/' + month + '/' + due.getFullYear();
                $('#id_expires').val(expires);
                $('#id_expires_picker').datepicker('update', expires);
            });
        }
    }
}]);