(function(global) {
    'use strict';

    // DOM convenience functions, from Barnaby Walters (waterpigs.co.uk)
    function first(selector,context){return(context||document).querySelector(selector);}
    function all(selector,context){return(context||document).querySelectorAll(selector);}
    function each(els,callback){return Array.prototype.forEach.call(els,callback);}
    function map(els,callback){return Array.prototype.map.call(els,callback);}

    function loadBroccoli() {
        var container = first('#broccoli-comments')
        if (container) {
            var user = container.dataset.user;
            var post = container.dataset.post;
            var iframe = document.createElement('iframe');
            iframe.src = ('{{url_for("embed.comments", _external=True)}}?user='
                          + encodeURIComponent(user) + '&post=' + encodeURIComponent(post));
            iframe.id = 'broccoli-iframe';
            iframe.width = '100%';
            iframe.scrolling = 'no';
            iframe.horizontalscrolling = 'no';
            iframe.verticalscrolling = 'no';
            iframe.frameborder = '0';
            iframe.style.width = '100%';
            iframe.style.border = 'none';
            iframe.style.overflow = 'hidden';
            container.appendChild(iframe);
        }
    }

    window.addEventListener('message', function(e) {
        var iframe = first('#broccoli-iframe');
        var eventName = e.data[0];
        var value = e.data[1];

        switch(eventName) {
        case 'setHeight':
            iframe.height = value + 'px';
            break;
        }
    }, false);

    loadBroccoli();

})(this);
