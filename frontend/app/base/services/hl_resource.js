angular.module('app.services').service('HLResource', HLResource);

HLResource.$inject = ['$injector', 'Settings'];
function HLResource($injector, Settings) {
    this.patch = function(model, args) {
        return $injector.get(model).patch(args, function() {
            toastr.success('I\'ve updated the ' + model.toLowerCase() + ' for you!', 'Done');
        }, function() {
            toastr.error('Something went wrong while saving the field, please try again.', 'Oops!');
            // For now return an empty string, we'll implement proper errors later.
            return '';
        });
    };

    /**
     * Gets the options for the given field which can be used for selects.
     * @param model {string}: The model that's loaded.
     * @param field {string}: The field for which the values will be retrieved.
     *
     * @returns: values {Array}: The retrieved values.
     */
    this.getChoicesForField = function(model, field) {
        // Dynamically get resource.
        var resource = $injector.get(model);
        var convertedField = _convertVariableName(field);
        var key;

        if (!resource.hasOwnProperty(convertedField)) {
            // Resource doesn't contain the given field.
            // So the field is probably a plural version of the given field or whatever.
            for (key in resource) {
                if (key.indexOf(convertedField) > -1) {
                    return resource[key]();
                }
            }
        } else {
            // Call the proper endpoint/field.
            return resource[convertedField]();
        }
    };

    /**
     * Creates an object with the data the object will be patched with.
     * @param data: The changed data. Can be an object or just a value.
     * @param [field] {string}: What field the data will be set to.
     * @param [model] {Object}: The model from which data can be retrieved.
     *
     * @returns args {Object}: The data the object will be patched with.
     */
    this.createArgs = function(data, field, model) {
        var args;

        if (typeof data === 'object') {
            args = data;
        } else {
            args = {
                id: model.id,
            };

            args[field] = data;

            if (field === 'name') {
                Settings.page.setAllTitles('detail', data);
            }
        }

        return args;
    };

    /**
     * Converts the given variable name so it can be used to retrieve a field of the given resource.
     * @param name {string}: The string that will be converted to camelCase.
     *
     * @returns {string}: The converted variable name.
     */
    function _convertVariableName(name) {
        var splitName = name.split('_');
        var convertedName = 'get';
        var i;

        // Convert to title case.
        for (i = 0; i < splitName.length; i++) {
            convertedName += splitName[i].charAt(0).toUpperCase() + splitName[i].slice(1);
        }

        return convertedName;
    }
}
