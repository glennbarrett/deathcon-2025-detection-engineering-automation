# Objective
This detection identifies usage of the ping command against Google.com

# Query
```js
index=main EventCode=1 Image="*\\ping.exe" CommandLine="*google.com*"
```
# Test Case
```sh
ping google.com
```

# Techniques
T1557.001, T1557.002

# References
https://google.com