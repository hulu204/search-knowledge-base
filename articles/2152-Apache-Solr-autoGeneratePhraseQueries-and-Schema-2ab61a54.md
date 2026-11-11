---
title: 'Apache Solr autoGeneratePhraseQueries and Schema'
company: Sease
tag: 查询理解
date: 2024-12-12
url: https://sease.io/2024/12/solr-autogeneratephrasequeries-schema-version.html
account: 
origin: harvest3-202607
---
In the Solr schema file, the XML tag `schema` contains two attributes: `name` and `version`.

```
				
					&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;schema name="my_schema" version="1.5"&gt;
	&lt;field name="_version_" type="long" indexed="true" stored="true" /&gt;
	&lt;field name="name" type="string" indexed="true" stored="false"/&gt;
        . . . 
&lt;/schema&gt;
				
			
```

You may think the schema version is an attribute useful for the admin to track the schema updates but you need to be aware that Solr adds some logic based on this value. Indeed, as you can see in the example below ([GitHub link](https://github.com/apache/solr/blob/661b1dac2284ab556573605ae81a4951a5703c49/solr/core/src/java/org/apache/solr/schema/TextField.java#L74-L78)), the schema version is used to determine the default of the parameter `autoGeneratePhraseQueries`. Logic introduced with [this Jira issue](https://issues.apache.org/jira/browse/SOLR-2519).

```
				
					if (schema.getVersion() &gt; 1.3F) {
  autoGeneratePhraseQueries = false;
} else {
  autoGeneratePhraseQueries = true;
}
				
			
```

## My experience

In a project I was using the attribute schema **version**, to keep track of the schema changes for development purposes and the latest version was the arbitrary value of `0.4`.  
I didn’t think this specific value would have consequences on internal Solr logic but actually does.  
For a specific field, I needed to omit the term frequency and position so, for each query involving that field, I got an error because the phraseQuery was not possible without the position.  
I was scratching my head as I was not running any explicit phrase query!  
Something was going on under the hood and I realised the culprit was the implicit default, caused by the logic described above.  
The issue was solved by explicitly defining the parameter **`autoGeneratePhraseQueries=false`**.  
Problem solved!

## Need Help With This Topic?​​

If you’re struggling with autoGeneratePhraseQueries, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with autoGeneratePhraseQueries, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)