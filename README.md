# RunwayRef
A model that returns an originality index and the top N similar articles from runway history for a given fashion article.

Summary:



sadf


The first implementation would look something like the following:

1. Take an image of a model wearing the design, and feed it to the model
2. The model will segment the image, separating the clothing from everything that is not the clothing. The model will employ deep encoder/decoder architecture. Tiramisu comes to mind. The clothing will be the "foreground"
3. The model will perform classification on the clothing. 
4. Based on the category, the model will search through a subset of the reference clothing database, which has also been segmented and classified, and find the most similar articles of clothing, including designer name and year/season. Based on this information, a composite "originality index" will also be computed.
5. (1-5, concurrently) Webscraping to build the reference database, and searching for good labelled datasets to train the lower dense layers on. DeepFashion2 comes to mind.
