angular.module('app.notes').factory('NoteDetail', NoteDetail);

NoteDetail.$inject = ['$resource'];
function NoteDetail($resource) {
    var _noteDetail = $resource(
        '/api/notes/:id',
        {
            size: 100,
        },
        {
            get: {
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);
                    var obj = {};

                    if (jsonData && jsonData.hits && jsonData.hits.length > 0) {
                        obj = jsonData.hits[0];
                        return obj;
                    }
                    return null;
                },
            },
            query: {
                url: '/api/notes?page_size=:size&ordering=-date&filterquery=:filterquery',
                isArray: true,
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);
                    var objects = [];

                    if (jsonData && jsonData.results && jsonData.results.length > 0) {
                        jsonData.results.forEach(function(obj) {
                            var noteObject = $.extend(obj, {activityType: 'note', color: 'yellow'});
                            objects.push(noteObject);
                        });
                    }

                    return objects;
                },
            },
            totalize: {
                url: '/api/notes?page_size=0&filterquery=:filterquery',
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);

                    if (jsonData && jsonData.total) {
                        return {total: jsonData.total};
                    }

                    return {total: 0};
                },
            },
        }
    );
    return _noteDetail;
}
