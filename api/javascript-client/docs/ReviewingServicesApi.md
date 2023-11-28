# EarlyEvidenceBaseApi.ReviewingServicesApi

All URIs are relative to *https://eeb.embo.org/api/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**reviewingServicesGet**](ReviewingServicesApi.md#reviewingServicesGet) | **GET** /reviewing_services/ | Get information about available reviewing services

<a name="reviewingServicesGet"></a>
# **reviewingServicesGet**
> ReviewingServiceCollection reviewingServicesGet()

Get information about available reviewing services

### Example
```javascript
import {EarlyEvidenceBaseApi} from 'early_evidence_base_api';

let apiInstance = new EarlyEvidenceBaseApi.ReviewingServicesApi();
apiInstance.reviewingServicesGet((error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ReviewingServiceCollection**](ReviewingServiceCollection.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

