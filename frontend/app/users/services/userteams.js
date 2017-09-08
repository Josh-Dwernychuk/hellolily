angular.module('app.users.services').factory('UserTeams', UserTeams);

UserTeams.$inject = ['$resource'];
function UserTeams($resource) {
    var _userTeam = $resource(
        '/api/users/team/:id/',
        null,
        {
            query: {
                isArray: false,
            },
            search: {
                url: '/api/users/team/',
                method: 'GET',
                transformResponse: function(data) {
                    let jsonData = angular.fromJson(data);
                    let objects = [];
                    let total = 0;

                    if (jsonData) {
                        if (jsonData.results && jsonData.results.length > 0) {
                            jsonData.results.forEach(function(obj) {
                                objects.push(obj);
                            });
                        }

                        total = jsonData.pagination.total;
                    }

                    return {
                        objects: objects,
                        total: total,
                    };
                },
            },
            mine: {
                method: 'GET',
                url: '/api/users/team/mine/',
                isArray: true,
            },
        }
    );

    return _userTeam;
}
