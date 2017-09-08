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
                url: '/api/notes?ordering=-created',
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
        }
    );
    return _noteDetail;
}
