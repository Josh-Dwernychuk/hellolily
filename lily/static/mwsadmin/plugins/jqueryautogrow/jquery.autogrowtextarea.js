/*!
    	return this.each(function(){
    	    
    	    if (options.cols)
    	        this.cols = options.cols;
    	    if (options.rows)
                this.rows = options.rows;
            
    		// Variables
    		var colsDefault = this.cols;
    		var rowsDefault = this.rows;
    		
    		//Functions
    		var grow = function() {
    			growByRef(this);
    		}
    		
    		var growByRef = function(obj) {
    			var lines = obj.value.split('\n');
                var linesCount = lines.length;
    			
    			var maxLineWidth = parseInt(obj.style.width);
    			for (var i=lines.length-1; i>=0; --i)
    			{
    			    if( lines[i].length > 0) {
                        linesCount += Math.floor( lineWidth / maxLineWidth );
    			    }
    			}
                
    			if (linesCount >= rowsDefault)
    				obj.rows = linesCount + 1;
    			else
    				obj.rows = rowsDefault;
    			
    			obj.style.height = ( parseInt($(obj).css('padding-bottom')) + parseInt($(obj).css('padding-top')) ) + (( obj.rows - 1) *  parseInt($(obj).css('line-height')) )  + 'px';
    		}
    		
    		var characterWidth = function (obj){
                var characterWidth = 0;
                var temp1 = 0;
                var temp2 = 0;
                var tempCols = obj.cols;
                
                obj.cols = 1;
                temp1 = $(obj).getHiddenOffsetWidth();
                obj.cols = 2;
                temp2 = $(obj).getHiddenOffsetWidth();
                characterWidth = temp2 - temp1;
                obj.cols = tempCols;
                
                return characterWidth;
            }
    		
    		// Manipulations
    		this.style.width = "auto";
    		this.style.height = "auto";
    		this.style.overflow = "hidden";
            this.style.width = ((characterWidth(this) * this.cols) + 6) + "px";
    		this.onkeyup = grow;
    		this.onfocus = grow;
    		this.onblur = grow;
    		growByRef(this);
    	});