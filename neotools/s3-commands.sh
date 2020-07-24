# list current content approx. 12 months or so (note the final slash /):
aws s3 ls --request-payer requester s3://biorxiv-src-monthly/Current_Content/

# count number of archive of specific month (note the final slash /):
aws s3 ls --request-payer requester s3://biorxiv-src-monthly/Current_Content/June_2020/ | wc -l

# downloading the meca archive from the biorxiv S3 bucket
aws s3 cp --request-payer requester --recursive --exclude "*" --include "*.meca" s3://biorxiv-src-monthly/Current_Content/June_2020 .

aws s3 sync --request-payer requester --exclude "*" --include "*.meca" s3://biorxiv-src-monthly/Current_Content/July_2020 .

docker run --rm -it -v ~/.aws:/root/.aws --mount type=bind,source=/raid/lemberge/sd-graph/biorxiv/Current_Content/July_2020,target=/root/Current_Content/July_2020 amazon/aws-cli s3 sync --request-payer requester --exclude "*" --include "*.meca" s3://biorxiv-src-monthly/Current_Content/July_2020 ./Current_Content/July_2020 --dryrun 
