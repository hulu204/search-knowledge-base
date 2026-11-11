---
title: 'Apache Solr Facets and ACL Filters Using Tag and Exclusion'
company: Sease
tag: 工程相关
date: 2018-12-24
url: https://sease.io/2018/12/apache-solr-facets-and-acl-filters-using-tag-and-exclusion.html
account: 
origin: harvest3-202607
---
What happens with facets aggregations on fields when documents in the results have been filtered by Access Control Lists?  
In such scenarios, it is important to use the **facet mincount parameter**.  
That specifies the minimum count in the result set for a facet value to appear in the response:

* + **mincount=0**, all the facet values present in the corpus are returned in the response. This includes the ones related to documents that have been filtered out by the ACLs(0 counts facets). This could cause some nasty side effects: such as a user seeing a facet value that he/she’s not supposed to see(because ACL filtered out that document from the result set).
  + **mincount=1**, only facet values matching at least one document in the result set are returned. This configuration is safe, users are going to see only facet values regulated by the ACL. They will effectively see only what they are supposed to see.

But what happens if you like to see 0 counting facet values, but preserving ACL?   
This may help you in having a better understanding of the distribution of the values in the entire corpus, but ACL are still valid so that users still see only possible values that they are supposed to see.  
Tags and Exclusion come in handy in such cases.

## Faceting Tag And Exclusion

Tag and Exclusion is an extremely important feature for faceting in Apache Solr and you would not believe how many times it is misused or completely ignored, causing an erratic experience for the user.  
Let’s see how it works:

##### Tagging

You can tag a filter query using Solr local parameter syntax:

```
				
					fq={!tag=docTypeFilter}doctype:pdf
				
			
```

The same applies to the main query(with some caveats if you are using an explicit query parser):

```
				
					q={!tag=mainQuery}I am the main query

q={!edismax qf=text title tag=mainQuery}I am the main query
				
			
```

When assigning a tag we give Solr the possibility of identifying separately the various search clauses (such as the main query or filter queries).  
Effectively it is a way to assign an identifier to a search query or filter.

##### Excluding in Legacy Faceting

When applying filter queries, Solr reduces the result space eliminating documents that don’t satisfy the additional filters added.  
Let’s assume we want to count the values for a facet on the result set, ignoring the additional filtering that was added by a filter query.  
Effectively can be equivalent to the concept of counting the facet values on a result set status that precedes the application of the filter that reduced the result set.  
Apache Solr allows you to do that, without affecting the final results returned.

This is called exclusion and can be applied on a facet-by-facet basis.

```
				
					fq={!tag=docTypeFilter}doctype:pdf...&amp;facet=true&amp;
facet.field={!ex=docTypeFilter}doctype
				
			
```

This will calculate the ‘doctype’ field facet on the result set with the exclusion of the tagged filter (so for the matter of calculating such aggregation the “doctype:pdf” filter will not be applied and the counts will be calculated on an extended result set).  
All other facets, aggregations and the result set itself will not be affected.

```
				
					1.&lt;Wanted Behaviour - applying tag and exclusion&gt;
=== Document Type ===   
[ ] Word (42)   
[x] PDF  (96)   
[ ] Excel(11)   
[ ] HTML (63)
				
			
```

This is especially useful for single-valued fields:  
when selecting a facet value and refreshing the search if you don’t apply tag and exclusion you will get just that value in the facets, defeating the refinement and exploration facet functionality for that field.

```
				
					2.&lt;Unwanted Behaviour - out of the box&gt;
=== Document Type ===   
[ ] Word (0)   
[x] PDF  (96)   
[ ] Excel(0)   
[ ] HTML (0)
				
			
```

```
				
					3.&lt;Unwanted Behaviour - mincount=1&gt;
=== Document Type ===     
[x] PDF  (96) 
				
			
```

As you see in 2. and 3. the facet becomes barely usable to further explore the results, this may cause the user experience to be fragmented with a lot of back-and-forth activity selecting and unselecting filters.

##### Excluding in Json Faceting

After the tagging of a filter, apply an exclusion with the json.facet approach is quite simple:

```
				
					visibleValues: {
     type: terms,
     field: cat,
     mincount: 1,
     limit: 100,
     domain: {
         excludeTags: &lt;tag&gt;
     }
 }
				
			
```

When defining a JSON facet, applying exclusion is just adding the domain node with the excludeTags defined.

## Tag and Exclusion to Preserve Acl Filtering in 0 counts

##### Problem

* + Users are subject to a set of ACL that limit their results visibility.
  + They would like to see also 0 count facets to have a better understanding of the result set and corpus.
  + You don’t want to invalidate the ACL control, so you don’t expect them to see sensible facet values.

##### Tagging the Main Query and Json Faceting

This is achievable with a combination of tagging and exclusion with JSON faceting.  
First of all, we want to tag the main query.  
We assume the ACL control will be a filter query (and we recommend applying ACL filtering with properly tuned filter queries).  
Tagging the main query and excluding it from the facet calculation will allow us to get all the facet values in the ACL-filtered corpus (the main query will be excluded but the ACL filter query will still be applied).

```
				
					q={!edismax tag=mainQuery qf=name}query&amp;fq=aclField:user1...
json.facet={visibleValues: {
     type: terms,
     field: cat,
     mincount: 1,
     limit: 100,
     domain: {
         excludeTags: mainQuery
     }
 }}
				
			
```

We are almost there, this facet aggregation will give the counts of all facet values visible to the user in the original corpus(with ACL applied).  
But what we want is to have the correct counts based on the current result set and all the visible 0 count facets.  
To do that we can add a block to the Json faceting request:

```
				
					q={!edismax tag=mainQuery qf=name}query&amp;fq=aclField:user1...
json.facet={
     resultSetCounts: {
         type: terms,
         field: category,
         mincount: 1
     },
     visibleValues: {
         type: terms,
         field: category,
         mincount: 1,
         domain: {
             excludeTags: mainQuery
         }
     }
 }
				
			
```

* + **resultSetCounts**–  are the counts in the result set, including only NOT 0 counts facet values. This is the list of values the user has visibility on the current result set with correct counts.
  + **visibleValues**– are all the facet values in the result set the user should have visibility

Then, depending on the user experience we want to provide, we could use these blocks of information to properly render a final response.  
For example, we may want to show all visible values and associate with them a count from the resultSetCounts when available.

```
				
					=== Document Type - Result Counts ===   
[ ] Word (10)   
[ ] PDF  (7)   
[ ] Excel(5)   
[ ] HTML (2)

=== Document Type - Visible Values ===   
[ ] Word (100)   
[ ] PDF  (75)   
[ ] Excel(54)   
[ ] HTML (34)
[ ] Jpeg (31)   
[ ] Mp4  (14)
 [ ] SecretDocType1 (0) -&gt; not visible, mincount=1 in visibleValues
 [ ] SecretDocType2 (0) -&gt; not visible, mincount=1 in visibleValues

=== Document Type - Final Result for users ===   
[ ] Word (10) -&gt; count is replaced with effective result count  
[ ] PDF  (7)  -&gt; count is replaced with effective result count 
[ ] Excel(5)  -&gt; count is replaced with effective result count
[ ] HTML (2)-&gt; count is replaced with effective result count
[ ] Jpeg (+31)   
[ ] Mp4  (+14)
				
			
```

##### Bonus: What if I Defined the Query Parser in the Solrconfig.xml

This solution is still valid if you are using your query parser defined in the solrconfig.xml.  
Extra care is needed to tag the main query.  
You can achieve that using the local params in Solr request parameters:

```
				
					solrconfig.xml
&lt;lst name="defaults"&gt;
...
&lt;str name="q"&gt;{!type=edismax tag=mainQuery v=$qq}&lt;/str&gt;
&lt;str name="qq"&gt;*:*&lt;/str&gt;
...

Query Time
.../solr/techproducts/browse?qq=ipod mini&amp;fq=acl:user1&amp;json.facet=...
				
			
```

Hope this helps when dealing with ACL or generic filter queries and faceting!

## Need Help With This Topic?​​

If you’re struggling with Solr Facets and ACL Filters, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Solr Facets and ACL Filters, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)