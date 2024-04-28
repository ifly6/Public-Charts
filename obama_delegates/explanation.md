NYT archive has table of delegates by date, state, and who won them. I scrape that using Pandas and give cumulative sum, then group by date to eliminate different states happening at different times.

Obama is ahead by 111 delegates after 11 March 2008.

![](https://i.redd.it/0mj67cpimhm41.png)

Cumulative sum of delegates is like this:

![](https://i.redd.it/zys1g32lmhm41.png)

Superdelegate information is hard to get, but is available on FiveThirtyEight in chart form [here](https://fivethirtyeight.com/features/superdelegates-might-not-save-hillary-clinton/). Obama was down in superdelegate terms by about 50, so if you add that against his lead, then you will still have him ahead by 60 or so.

According to the CSV that was produced, also in this respository, Obama wasn't behind Clinton in pledged delegate terms at any point after 19 January. Lacking superdelegate data, I can only ballpark, but he wasn't behind in March.
