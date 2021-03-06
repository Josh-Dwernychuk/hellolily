angular.module('app.directives').directive('featureUnavailable', featureUnavailable);

function featureUnavailable() {
    return {
        restrict: 'E',
        scope: {
            tier: '@',
            labelIcon: '@?',
            labelText: '@?',
        },
        templateUrl: 'base/directives/feature_unavailable.html',
        replace: true,
        transclude: true,
    };
}
