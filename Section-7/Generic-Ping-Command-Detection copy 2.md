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
T1134.002, T1134.001, T1485, T1070.003

# References
https://google.com