from fastapi import HTTPException, status

redis_connection_exception = HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                                          detail="Redis database connection cannot be established.",
                                            headers={"Retry-After": "60"})

twitter_timeout_exception = HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                                detail="Oauth service took too long to respond. Please try again.")

twitter_bad_gateway_exception = HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, 
                            detail="Failed to connect to oauth provider.")