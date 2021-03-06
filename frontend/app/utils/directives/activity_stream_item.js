angular.module('app.utils.directives').directive('activityStreamItem', ActivityStreamItemDirective);

ActivityStreamItemDirective.$inject = ['$compile', '$http', '$templateCache'];
function ActivityStreamItemDirective($compile, $http, $templateCache) {
    return {
        restrict: 'E',
        scope: {
            item: '=',
            activity: '=',
            object: '=',
            deleteCallback: '&?',
            updateCallback: '&?',
        },
        link: function(scope, element, attrs) {
            var getTemplate = function(activityType) {
                var templateLoader;
                var baseUrl = 'utils/directives/activity_stream_';
                var templateMap = {
                    case: 'case.html',
                    deal: 'deal.html',
                    email: 'email.html',
                    note: 'note.html',
                    call: 'call.html',
                    change: 'change.html',
                };

                var templateUrl = baseUrl + templateMap[activityType];
                templateLoader = $http.get(templateUrl, {cache: $templateCache});

                return templateLoader;
            };
            getTemplate(scope.vm.item.activityType).success(function(html) {
                element.replaceWith($compile(html)(scope));
            }).then(function() {
                element.replaceWith($compile(element.html())(scope));
            });
        },
        controller: ActivityStreamItemController,
        bindToController: true,
        controllerAs: 'vm',
    };
}

ActivityStreamItemController.$inject = ['$scope', '$state'];
function ActivityStreamItemController($scope, $state) {
    var vm = this;

    vm.replyOnEmail = replyOnEmail;
    vm.removeFromList = removeFromList;

    /////

    function replyOnEmail() {
        // Check if the emailaccount belongs to the current contact or account.
        angular.forEach(vm.object.email_addresses, function(emailAddress) {
            if (emailAddress.email_address === vm.item.sender_email && emailAddress.status === 0) {
                // Is status is inactive, try to find other email address.
                _replyToGoodEmailAddress();
            }
        });

        function _replyToGoodEmailAddress() {
            // Try to find primary.
            angular.forEach(vm.object.email_addresses, function(emailAddress) {
                if (emailAddress.status === 2) {
                    $state.go('base.email.replyOtherEmail', {id: vm.item.id, email: emailAddress.email_address});
                }
            });

            // Other will do as alternative.
            angular.forEach(vm.object.email_addresses, function(emailAddress) {
                if (emailAddress.status === 1) {
                    $state.go('base.email.replyOtherEmail', {id: vm.item.id, email: emailAddress.email_address});
                }
            });
        }

        $state.go('base.email.reply', {id: vm.item.id});
    }

    function removeFromList(deletedNote) {
        vm.item.notes = vm.item.notes.filter(note => note.id !== deletedNote.id);

        $scope.$apply();
    }
}
