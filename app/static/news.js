// news.js
/*global $:false, location: false */
/*jslint unparam: true*/
var moment;
var news = {};
var window, document;

news.showAdvStatuses = function (text) {
    var root, url;
    root = $(location).attr('href');
    url = root + 'statuses/' + encodeURIComponent(text);
    window.history.pushState({'id': 'root'}, '', root);
    location.href = url;
};

// sets up the datepicker element
$(function () {
    function cb (start, end) {
	$('#reportrange span').html('Set custom date range');
    }
    cb(moment().subtract(2, 'days'), moment().subtract(1, 'days'));

    $('#reportrange').daterangepicker({
	'autoApply': true,
	'showDropdowns': true,
	'startDate': moment().subtract(2, 'days'),
	'endDate': moment(),
	'minDate': '08/01/2015',
	ranges: {
	    'Yesterday': [moment().subtract(2, 'days'),
			  moment().subtract(1, 'days')],
	    'Past 7 days': [moment().subtract(7, 'days'), moment()],
	    'Past 14 Days': [moment().subtract(14, 'days'), moment()],
	    'This Month': [moment().startOf('month'), moment().endOf('month')],
	    'Last Month': [moment().subtract(1, 'month').startOf('month'),
			   moment().subtract(1, 'month').endOf('month')]
	}
    }, cb);
});

// opens up the datepicker if the custom date button is clicked
$('.time').click(function (event) {
    if (event.target.id === 'customdate') {
	$('.calendar').toggle();
	$('#reportrange').trigger('click');
    }
});

$('.tpc').click(function (event) {
    // make the topic div active
    $(this).toggleClass('activetpc');
});

$('.cat').click(function (event) {
    var cat;
    $(this).toggleClass('activecat');
    cat = $(this).attr('name');
    $('.' + cat).each(function (index) {
	$(this).toggleClass('activetpc');
    });
});

// build the query from the various parts
// if custom date has been set, take date from datepicker
// otherwise from value of the active date button

// MODIFIED from original design: to use only submit btn instead of or/and/single
news.buildQuery = function (op) {
    var date, query, text;
    date = $('.time > label.active input').val();
    if (date === '@') { // custom date has been set
	date = news.getCustomDate();
    }
    query = news.collectTerms(op);
    if (query !== 'none') {
	text = [date, query].join(' ');
	news.showAdvStatuses(text);
    }
};

news.collectTerms = function (op) {
    var terms = [];
    var nterms;
    var query = 'none';
    // get the custom query if any
    terms.push($('#custquery').val());
    $('.activetpc').each(function (index) {
	var name;
	name = $(this).attr('name');
	terms.push('*' + name);
    });
    nterms = terms.length;
    if (nterms < 1) {
	news.error('Please choose one or more topics');
    } else if (nterms > 1) {
	query = terms.join(' ');
    } else if (nterms === 1) {
	query = terms[0];
    }
    return query;
};

news.error = function (msg) {
    $('.errorbox').html(msg);
};

$('.logicbtn').click(function (event) {
    news.buildQuery($(this).attr('id'));
});

// pressing enter in custom query box emulates submit
$('#custquery').on('keydown', function(e) {
    if (e.which == 13){
	news.buildQuery($('#submit'));
    }
});

news.getCustomDate = function () {
    var start, end, date;
    var picker;
    picker = $('#reportrange').data('daterangepicker');
    start = picker.startDate.format('YYYY-MM-DD');
    end = picker.endDate.format('YYYY-MM-DD');
    date = '-s ' + start + ' -e ' + end;
    return date;
};

$('#reportrange').on('apply.daterangepicker', function (ev, picker) {
    var start, end;
    $('#reportrange span').html('date range selected');
    start = picker.startDate.format('YYYY-MM-DD');
    end = picker.endDate.format('YYYY-MM-DD');
    news.datepart = '-s ' + start + ' -e ' + end;
});

$(document).ready(function () {
    $('.calendar').hide();
});
