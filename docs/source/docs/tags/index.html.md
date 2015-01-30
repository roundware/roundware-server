---
page_title: "Tags"
sidebar_current: "tags"
---

# Roundware Tags

One of the powerful features of Roundware is its tagging capability.  Tags are used to assign
metadata to assets, primarily for filtering, but also for archival purposes.  Roundware tags
are grouped by `tag_category`, for example, the tags `young` and `old` could be tags within the `age` `tag_category`.

Tags and tag categories are very flexible and can be setup however makes the most sense for a project.  Each asset within a project
should be assigned at least one tag from each available tag category for the project in order for the
filtering to work properly.

Tags are initially assigned to assets when they are added to the system, either through the admin or by a participant via a client.
Tags can be edited thereafter, of course, using the admin.  Participants select a tag from each tag category
as part of the contribution process.  It is advisable to not require participants to select too many
tags for their contributions, so most Roundware projects have between 2-3 tag categories.

Also see more info on [Tag Setup](../setup/tag.html) and [Tag Admin](../admin/tag.html).

### Tag Filtering

Since tags are grouped by ```tag_category```, the filtering mechanism becomes slightly more complex than a
simple AND or OR filter of tag ids.

* Within each ```tag_category```, filters work as an OR filter such that any asset tagged with any one of the
tag ids passed is included.
* Between the represented ```tag_categories```, filtering is done with an AND filter.
* Any ```tag_category``` not represented by any of the tag ids present in the request will be ignored entirely such
that no further filtering occurs per that ```tag_category```.

#### Example

Let's say we have three tag categories and respective tag ids: ```gender``` [tag ids 1, 2], ```age``` [tag ids 3, 4], and ```question``` [tag ids 5, 6].
And we have two assets:

*Asset A* - tag ids 1, 3, 5

*Asset B* - tag ids 2, 4, 5

<table class="table table-striped table-bordered mr-types">
    <thead>
        <tr>
            <th>Tag id parameters</th>
            <th>Boolean interpretation</th>
            <th>Assets returned</th>
            <th>Notes</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1, 3, 4, 5, 6</td>
            <td>1 AND (3 OR 4) AND (5 OR 6)</td>
            <td>B</td>
            <td>even though B contains tag ids 4 and 5, since it doesn't include tag id 1, it is filtered out</td>
        </tr>
        <tr>
            <td>1, 4, 5</td>
            <td>1 AND 4 AND 5</td>
            <td>NONE</td>
            <td>no assets are returned despite the fact that assets exist with each of the individual tags passed;
                one from each tag category is not matched in any available asset, hence nothing returned</td>
        </tr>
        <tr>
            <td>1, 2, 3, 4, 6</td>
            <td>(1 OR 2) AND (3 OR 4) AND 6</td>
            <td>NONE</td>
            <td>neither A nor B contain tag id 6, so nothing is returned</td>
        </tr>
        <tr>
            <td>1, 2, 3, 4</td>
            <td>(1 OR 2) AND (3 OR 4)</td>
            <td>A, B</td>
            <td>question tag category is ignored entirely as no tag id in the category was passed</td>
        </tr>
    </tbody>
</table>

### Tag Relationships

Tags can be related to each other in order to create tag hierarchies.  For example, say there is a project with two
tag categories:

**demographic**: `child` `adult`

**question**: `What college did you attend?` `Why is there food all over your face?` `Make up a story.`

You want to ask adults about college and stories, but not food, and you want to ask kids about food and stories, but not college.
You can use tag relationships to link the `child` tag to `Why is there food all over your face?` and `Make up a story.` and
the `adult` tag to `What college did you attend?` and `Make up a story.`  This will cause the user interface to present a different
set of questions depending on which demographic is chosen.  Obviously, one must ensure that the ordering of the tag categories
is set properly so that `demographic` is presented to the user prior to `question`.

### Tag Data

The `tag.data` field is a temporary field.  Currently, it is
being used to set the html class of the tag for display in the tag webviews, for example `class=tag-one`.

We intend to expand the tags data from a field into a new `tag_data` model such that an arbitrary number of additional
pieces of data can be stored with a tag.  This becomes very useful for situations such as when a tag is used
to indicate an object that has a physical location (i.e. a sculpture in a sculpture park).  In these situations,
tag data of types `latitude` and `longitude` could be created and used for a multitude of purposes within the
clients and back-end.

<!-- <div class="alert alert-block alert-info">
<p>
<strong>More of a book person?</strong> If you prefer to read a physical
book, you may be interested in
<a href="http://www.amazon.com/gp/product/1449335837/ref=as_li_qf_sp_asin_il_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=1449335837&linkCode=as2&tag=vagrant-20">
Vagrant: Up and Running
</a>, written by the author of Vagrant and published by O'Reilly.
</p>
</div> -->
