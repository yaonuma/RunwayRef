# RunwayRef
A model that returns an originality index and the top N similar articles from runway history for a given fashion article.

Summary:

Creative products are rarely totally original. Some famous people agree:

"Art is theft." - Pablo Picasso

"The only art I’ll ever study is stuff that I can steal from.” - David Bowie

"My hobbie (one of them anyway)…is using a lot of scotch tape… 
My hobbie is to pick out different things during what I read 
and piece them together and make a little story of my own.” - Louis Armstrong

Louis Armstrong's framing of the creative process captures the subtlety of this project's intention. That is, RunwayRef's originality index and list of similar fashion designs from the past isn't targeted at "cancelling" designers, but rather to aid in the early stages of the design process - to help the designer tape together pieces from different stories to create a new one. The business interest would be more rapid design prototyping with a higher degree of integrity.

The first attempt implementation would look something like the following, at a high level:

1. Take an image of a model wearing the design, and feed it to the model
2. The model will segment the image, separating the clothing from everything that is not the clothing. The model will employ deep encoder/decoder architecture. Tiramisu comes to mind. The clothing will be the "foreground"
3. The model will perform classification on the clothing. 
4. Based on the category, the model will search through a subset of the reference clothing database, which has also been segmented and classified, and find the most similar articles of clothing, including designer name and year/season. Based on this information, a composite "originality index" will also be computed.
5. (1-5, concurrently) All meanwhile, webscraping to build the reference database, and searching for good labelled datasets to train the lower dense layers on. DeepFashion2 comes to mind.
