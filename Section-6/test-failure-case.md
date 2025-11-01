# Objective
This detection identifies usage of the ping command against Google.com

# Query
```js
index=main EventCode=1 Image="*\\ping.exe" CommandLine="*googgle.com*"
```
# Test Case
```sh
ping google.com
```

# References
https://google.com