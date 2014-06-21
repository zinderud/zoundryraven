<?xml version="1.0" encoding="UTF-8"?>
<xsl:transform xmlns:zns='http://www.zoundry.com/schemas/2006/05/zdocument.rng'
    xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='1.0'>

    <!-- Converts top level entry attributes, trackback attributes, and categories to the new attribute format. -->
    <xsl:template match="/entry/* | /entry/trackback/* | /entry/postcategories/forblog/categories/category/*">
        <zns:attribute>
            <xsl:attribute name="name">
                <xsl:value-of select="local-name()"/>
            </xsl:attribute>
            <xsl:value-of select="text()"/>
        </zns:attribute>
    </xsl:template>

    <!-- Converts custom publish-info attributes to the new attribute format. -->
    <xsl:template match="/entry/published/publish-info/attribute[starts-with(@name, 'cms:')]" priority="1">
        <zns:attribute>
            <xsl:attribute name="name"><xsl:value-of select="substring(@name, 5)"/></xsl:attribute>
            <xsl:attribute name="namespace">urn:zoundry:cms</xsl:attribute>
            <xsl:value-of select="text()"/>
        </zns:attribute>
    </xsl:template>
    <xsl:template match="/entry/published/publish-info/attribute[starts-with(@name, 'atom-')]" priority="1">
        <zns:attribute>
            <xsl:attribute name="name"><xsl:value-of select="substring(@name, 6)"/></xsl:attribute>
            <xsl:attribute name="namespace">urn:zoundry:atom</xsl:attribute>
            <xsl:value-of select="text()"/>
        </zns:attribute>
    </xsl:template>
    <xsl:template match="/entry/published/publish-info/attribute" priority="0">
        <zns:attribute>
            <xsl:attribute name="name"><xsl:value-of select="@name"/></xsl:attribute>
            <xsl:value-of select="text()"/>
        </zns:attribute>
    </xsl:template>

    <!-- Converts categories to the new category format. -->
    <xsl:template match="/entry/postcategories/forblog/categories/category">
        <zns:category>
            <zns:attributes>
                <xsl:apply-templates select="*" />
            </zns:attributes>
        </zns:category>
    </xsl:template>

    <!-- Converts the old publish-info sections to the new blog/publish-info section. -->
    <xsl:template match="/entry/published/publish-info">
        <xsl:variable name="BLOGID" select="@blog-id" />
        <!-- Create a top level element called "blog" to hold all meta information for a single blog. -->
        <zns:blog>
            <xsl:attribute name="account-id">
                <xsl:value-of select="@account-id"/>
            </xsl:attribute>
            <xsl:attribute name="blog-id">
                <xsl:value-of select="@blog-id"/>
            </xsl:attribute>
            <!-- Copy of the publish-info stuff as attributes. -->
            <zns:publish-info>
                <zns:attributes>
                    <zns:attribute>
                        <xsl:attribute name="name">blog-entry-id</xsl:attribute>
                        <xsl:value-of select="@blog-entry-id"/>
                    </zns:attribute>
                    <zns:attribute>
                        <xsl:attribute name="name">id</xsl:attribute>
                        <xsl:value-of select="@id"/>
                    </zns:attribute>
                    <xsl:apply-templates select="attribute[not(starts-with(@name, 'trackback-'))]"/>
                </zns:attributes>
                <!-- Hack in a section for trackbacks (there is only 1 in the 1.x data, but there may be multiple in Raven). -->
                <xsl:if test="attribute[starts-with(@name, 'trackback-')]">
                    <zns:trackbackrefs>
				         <zns:trackbackref>
				             <zns:attributes>
				             	<zns:attribute name="url"><xsl:value-of select="attribute[@name='trackback-sent-url']/text()"></xsl:value-of></zns:attribute>
				                <zns:attribute name="sent-date"><xsl:value-of select="attribute[@name='trackback-sent-date']/text()"></xsl:value-of></zns:attribute>
				             </zns:attributes>
				         </zns:trackbackref>
                    </zns:trackbackrefs>
                </xsl:if>
            </zns:publish-info>
            <zns:categories>
                <xsl:apply-templates select="/entry/postcategories/forblog[@blog-id = $BLOGID]/categories/category"/>
            </zns:categories>
        </zns:blog>
    </xsl:template>
    
    <!-- Converts old tagwords to new tagwords. -->
    <xsl:template match="/entry/tagwordset/tagwords">
        <zns:tagwords>
            <xsl:attribute name="url"><xsl:value-of select="@url"></xsl:value-of></xsl:attribute>
            <xsl:value-of select="text()"></xsl:value-of>
        </zns:tagwords>
    </xsl:template>

    <!-- Converts old trackback section to the new format. -->    
    <xsl:template match="/entry/trackback">
         <zns:trackback>
             <zns:attributes>
                 <zns:attribute name="url"><xsl:value-of select="ping/text()"></xsl:value-of></zns:attribute>
             </zns:attributes>
         </zns:trackback>        
    </xsl:template>

    <!-- Matches the root element and begins the conversion to the new format. -->
    <xsl:template match="/entry">
        <zns:entry>
            <xsl:attribute name="entry-id">
                <xsl:value-of select="@id"/>
            </xsl:attribute>
            <zns:attributes>
                <xsl:apply-templates select="creation-time | modified-time | published-time | title | author | categories"/>
            </zns:attributes>
            <zns:blogs>
                <xsl:apply-templates select="published/*" />
            </zns:blogs>
            <zns:tagwordset>
                <xsl:apply-templates select="tagwordset/*" />
            </zns:tagwordset>
            <zns:trackbacks>
                <xsl:apply-templates select="trackback" />
            </zns:trackbacks>        		
            <zns:content type="application/xhtml+xml" />
        </zns:entry>
    </xsl:template>
    
</xsl:transform>
