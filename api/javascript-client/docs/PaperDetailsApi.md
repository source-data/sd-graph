# EarlyEvidenceBaseApi.PaperDetailsApi

All URIs are relative to *https://eeb.embo.org/api/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**papersGet**](PaperDetailsApi.md#papersGet) | **GET** /papers/ | Get paginated collections of papers, optionally filtered by reviewing service

<a name="papersGet"></a>
# **papersGet**
> InlineResponse200 papersGet(opts)

Get paginated collections of papers, optionally filtered by reviewing service

### Example
```javascript
import {EarlyEvidenceBaseApi} from 'early_evidence_base_api';

let apiInstance = new EarlyEvidenceBaseApi.PaperDetailsApi();
let opts = { 
  'reviewedBy': ["reviewedBy_example"], // [String] | The IDs of the reviewing services for which papers are requested.
  'query': "query_example", // String | A search string to filter the results by.
  'page': 1, // Number | The page number of the results to retrieve. The first page is 1.
  'perPage': 10, // Number | The number of results to return per page.
  'sortBy': "preprint-date", // String | The field to sort the results by.
  'sortOrder': "desc" // String | The direction to sort the results in.
};
apiInstance.papersGet(opts, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **reviewedBy** | [**[String]**](String.md)| The IDs of the reviewing services for which papers are requested. | [optional] 
 **query** | **String**| A search string to filter the results by. | [optional] 
 **page** | **Number**| The page number of the results to retrieve. The first page is 1. | [optional] [default to 1]
 **perPage** | **Number**| The number of results to return per page. | [optional] [default to 10]
 **sortBy** | **String**| The field to sort the results by. | [optional] [default to preprint-date]
 **sortOrder** | **String**| The direction to sort the results in. | [optional] [default to desc]

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

