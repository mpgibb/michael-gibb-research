# Workflow event data

Boudewijn van Dongen (2017): *BPI Challenge 2017*. Eindhoven University of Technology. [doi:10.4121/uuid:5f3067df-f10b-45da-b98b-86ae4c7a310b](https://doi.org/10.4121/uuid:5f3067df-f10b-45da-b98b-86ae4c7a310b), distributed by 4TU.ResearchData / [publisher record](https://figshare.com/articles/dataset/BPI_Challenge_2017/12696884).

The XES gzip contains 31,509 application traces and 1,202,267 events. Source SHA-256: `183c5e5189282779c811c78c33ff936351b3dd201165d612211fc220936f8249`; 29,658,747 bytes. First event 2016-01-01T09:51:15.304Z; final event 2017-02-01T14:11:03.499Z. The latter is 15:11 in the publisher's local winter time. Applications were filed during 2016, with later events retained through the cutoff.

Events distinguish application, offer and workflow origins. Workflow transitions include schedule, start, suspend, resume, complete, withdraw and ate_abort. There are 42,995 offer-creation events, so offer count is not application count. Source traces may contain post-disposition work-item events. The study's target is the first recorded A_Pending/A_Denied/A_Cancelled application status, not the final trace timestamp or actual funds disbursement.

Missing outcomes are right-censored at the relevant administrative cutoff. Raw application/resource/offer identifiers and all financial records remain external. Features describe only workflow history observed in the selected prefix. No person-level lending eligibility, pricing or approval recommendation is produced.

License: [4TU General Terms of Use (2016)](https://ndownloader.figshare.com/files/24080255) as linked by the publisher's license metadata. Preserve source attribution and noncommercial use; provide 4TU.ResearchData bibliographic details when publishing a result. No raw data are redistributed. Publication status remains separate from execution status while required notification is prepared.
