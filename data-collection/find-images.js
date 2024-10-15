/**** Start of imports. If edited, may not auto-convert in the playground. ****/
var geo = /* color: #d63000 */ee.Geometry.Polygon(
        [[[22.979379194653458, 42.75380946939111],
          [23.020577925122208, 42.61550793147515],
          [23.280129927075333, 42.39175962510198],
          [23.685250776684708, 42.406971490060414],
          [23.686624067700333, 42.62763423720577],
          [23.697610395825333, 42.85154479733822],
          [23.545175093090958, 42.87972833847439],
          [23.252664106762833, 42.93505140268155],
          [23.074136274731583, 42.88274724041879]]]);
/***** End of imports. If edited, may not auto-convert in the playground. *****/
var w_mul = 0.00341802;
var b_add = 149.0;

var table = ee.FeatureCollection("projects/ee-dianamarkovakn/assets/mygeodata"),
    geometry = geo;

var aoi = table;

var seasons = {
  'winter': [['01-01', '02-28'], ['12-01', '12-31']], // Winter range
  'spring': [['03-01', '05-31']], 
  'summer': [['06-01', '08-31']], 
  'autumn': [['09-01', '11-30']], 
  'winter-leap': [['01-01', '03-01'], ['12-01', '12-31']]
};

var periods = [
 // {'start': '1999-01-01', 'end': '1999-12-31', 'collection': 'LANDSAT_7' }, 
 // {'start': '2000-01-01', 'end': '2000-12-31', 'collection': 'LANDSAT_7'}, 
 // {'start': '2001-01-01', 'end': '2001-12-31', 'collection': 'LANDSAT_7'},
 // {'start': '1999-01-01', 'end': '1999-12-31', 'collection': 'LANDSAT_5' }, 
 // {'start': '2000-01-01', 'end': '2000-12-31', 'collection': 'LANDSAT_5'}, 
 // {'start': '2001-01-01', 'end': '2001-12-31', 'collection': 'LANDSAT_5'},
 // {'start': '2005-01-01', 'end': '2005-12-31', 'collection': 'LANDSAT_5'}, 
//  {'start': '2006-01-01', 'end': '2006-12-31', 'collection': 'LANDSAT_5'}, 
//  {'start': '2007-01-01', 'end': '2007-12-31', 'collection': 'LANDSAT_5'},
//  {'start': '2008-01-01', 'end': '2008-12-31', 'collection': 'LANDSAT_5'},
//  {'start': '2009-01-01', 'end': '2009-12-31', 'collection': 'LANDSAT_5'}, 
//  {'start': '2011-01-01', 'end': '2011-12-31', 'collection': 'LANDSAT_5'}, 
//  {'start': '2012-01-01', 'end': '2012-12-31', 'collection': 'LANDSAT_5'},
//  {'start': '2013-01-01', 'end': '2013-12-31', 'collection': 'LANDSAT_8'},
//  {'start': '2014-01-01', 'end': '2014-12-31', 'collection': 'LANDSAT_8'}, 
//  {'start': '2017-01-01', 'end': '2017-12-31', 'collection': 'LANDSAT_8'}, 
//  {'start': '2018-01-01', 'end': '2018-12-31', 'collection': 'LANDSAT_8'}, 
//  {'start': '2019-01-01', 'end': '2019-12-31', 'collection': 'LANDSAT_8'}, 
  
  {'start': '2020-01-01', 'end': '2020-12-31', 'collection': 'LANDSAT_8'},
  {'start': '2021-01-01', 'end': '2021-12-31', 'collection': 'LANDSAT_8'},
  {'start': '2022-01-01', 'end': '2022-12-31', 'collection': 'LANDSAT_8'},
  {'start': '2023-01-01', 'end': '2023-12-31', 'collection': 'LANDSAT_8'}, 
];

//Load Collection 2 Level 2 with ST bands 
var landsat5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2');
var landsat7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2');
var landsat8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2');

//var landsat5 = ee.ImageCollection('LANDSAT/LT05/C02/T2_L2');
//var landsat7 = ee.ImageCollection('LANDSAT/LE07/C02/T2_L2');
//var landsat8 = ee.ImageCollection('LANDSAT/LC08/C02/T2_L2');

// Function to filter images by season and year range and return metadata as FeatureCollection
function filterSeasonByYear(collection, startYear, endYear, startMonthDay, endMonthDay, season) {
  var start = ee.Date(startYear + '-' + startMonthDay);
  var end = ee.Date(endYear + '-' + endMonthDay);
  
  var filteredCollection = collection.filterDate(start, end)
                   .filterBounds(geo)
                   .filter(ee.Filter.lte('CLOUD_COVER', 10))
                   .filter(ee.Filter.contains({
                      leftField: '.geo',
                      rightValue: geo
                   }));
  
  // Create a FeatureCollection of image metadata
  var metadata = filteredCollection.map(function(image) {
    return ee.Feature(null, {
      'image_id': image.id(),
      'season': season,
      'cloud_cover': image.get('CLOUD_COVER'),
      'year': startYear
    });
  });
  
  return metadata;
}

// Function to get metadata for images in each season and period
function getSeasonalMetadata(period, season, collection, collection_id) {
  var startYear = period['start'].substring(0, 4); 
  var endYear = period['end'].substring(0, 4);
  
  var season_chosen = season;
  
  var year = parseInt(startYear, 10);  // Convert the string to an integer
  
  // Check if the year is a leap year
  var isLeapYear = (year % 4 === 0 && year % 100 !== 0) || (year % 400 === 0)
  
  if(isLeapYear && season === 'winter') {
    season_chosen = 'winter-leap';
    print('leap ' + startYear);
  }


  var seasonRanges = Array.isArray(seasons[season_chosen]) ? seasons[season_chosen] : [seasons[season_chosen]];
  
  var allMetadata = ee.FeatureCollection([]);

  seasonRanges.forEach(function(range) {
    var seasonMetadata = filterSeasonByYear(collection, startYear, endYear, range[0], range[1], season);
    allMetadata = allMetadata.merge(seasonMetadata);
  });
  
  return allMetadata;
}

// Initialize an empty FeatureCollection to store all metadata
var allMetadata = ee.FeatureCollection([]);

// Loop over periods and accumulate metadata
periods.forEach(function(period) {
  ['winter', 'spring', 'summer', 'autumn'].forEach(function(season) {
    var collection, collection_id;
    var startYear = period.start.substring(0, 4);
  
    
    if (period.collection == 'LANDSAT_5') {
      collection = landsat5;
      collection_id = 'LANDSAT_5';
    } else if (period.collection == 'LANDSAT_7') {
      collection = landsat7;
      collection_id = 'LANDSAT_7';
    } else if (period.collection == 'LANDSAT_8') {
      collection = landsat8;
      collection_id = 'LANDSAT_8';
    } else {
      print('No Landsat collection for year: ' + startYear);
      return;
    }
    
    // Get metadata for this season and add to the total collection
    var seasonalMetadata = getSeasonalMetadata(period, season, collection, collection_id);
    allMetadata = allMetadata.merge(seasonalMetadata);
  });
});

// Export the combined metadata to a single JSON file
Export.table.toDrive({
  collection: allMetadata,
  description: 'Landsat-All-Metadata-new-period',
  fileFormat: 'CSV',
  folder: 'Landsat-Metadata',
});
