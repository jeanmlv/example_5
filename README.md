# example_5

Hi Tiffany, thanks for the updates! The diagram looks much better and reflects our ARD workflow more accurately.

Just one small suggestion: in the IDAR box, I would mention that they support missing variable investigations by providing additional clinical datasets, study metadata (such as aCRFs and ADaM metadata), and variable mapping clarifications.

Regarding your questions:

1. **Domino:** I work directly in the Domino environment, where I import the available SDTM/ADaM datasets and run my scripts to generate and update the ARDs. The ARDs are then made available for the team through Thea.View.

2. **Thea.View:** Each ARD has a corresponding location in Thea.View, and we maintain these direct access links in our ARGES Commons inventory so the team can easily locate the ARDs.

However, I'm not entirely sure how permissions are managed internally in Thea.View or whether access is controlled at the project or individual asset level. We may need to confirm that with the platform team.

Overall, I think the updated diagram looks great!

Hi Tiffany, just to clarify your questions:

Domino: We have a Domino project called "cv_endoscopy", where I use my own workspace to import and process the clinical datasets (SDTM/ADaM), run my scripts, and generate the ARDs. So, although I work in my own workspace, the processing takes place within the Domino project environment.

Thea.View: The ARDs are organized within a collection, with separate folders for each clinical trial (e.g., STARDUST, POWER, GALAXI, QUASAR, etc.).

These folders are marked as "Private" in Thea.View, so access appears to be permission-controlled. However, I'm not entirely sure whether permissions are managed at the collection, folder, or user/group level.

We also maintain the direct links to these ARD locations in our ARGES Commons inventory, making it easier for the team to locate the corresponding ARDs for each study.

Hope this helps clarify how the data are organized across both platforms!
