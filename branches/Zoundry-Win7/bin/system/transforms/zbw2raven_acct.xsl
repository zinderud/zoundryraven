<?xml version="1.0" encoding="UTF-8"?>
<xsl:transform xmlns:zns='http://www.zoundry.com/schemas/2006/05/zaccount.rng'
    xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='1.0'>

    <!-- Converts top level account attributes to the new attribute format. -->
    <xsl:template match="/blog-account/* | /blog-account/blogs/blog/categories/category/* | /blog-account/api-info/*">
        <zns:attribute>
            <xsl:attribute name="name"><xsl:value-of select="local-name()"/></xsl:attribute>
            <xsl:value-of select="text()"/>
        </zns:attribute>
    </xsl:template>

    <xsl:template match="/blog-account/icon">
        <zns:attribute>
            <xsl:attribute name="name"><xsl:value-of select="local-name()"/></xsl:attribute>
            <xsl:value-of select="@resid"/>
        </zns:attribute>
    </xsl:template>

    <!-- Converts blog attributes to the new attribute format. -->
    <xsl:template match="/blog-account/blogs/blog/attribute[starts-with(@name, 'atom-')]" priority="1">
        <zns:attribute>
            <xsl:attribute name="name"><xsl:value-of select="substring(@name, 6)"/></xsl:attribute>
            <xsl:attribute name="namespace">urn:zoundry:atom</xsl:attribute>
            <xsl:value-of select="text()"/>
        </zns:attribute>
    </xsl:template>
    <xsl:template match="/blog-account/blogs/blog/attribute" priority="0">
        <zns:attribute>
            <xsl:attribute name="name"><xsl:value-of select="@name"/></xsl:attribute>
            <xsl:value-of select="text()"/>
        </zns:attribute>
    </xsl:template>
    
    <xsl:template match="/blog-account/blogs/blog/categories/category">
        <zns:category>
            <zns:attributes>
                <xsl:apply-templates select="*" />
            </zns:attributes>
        </zns:category>
    </xsl:template>

    <!-- Converts old blog entries to the new format. -->
    <xsl:template match="/blog-account/blogs/blog">
        <zns:blog>
            <xsl:attribute name="blog-id"><xsl:value-of select="id" /></xsl:attribute>
            <zns:attributes>
                <zns:attribute>
                    <xsl:attribute name="name">name</xsl:attribute>
                    <xsl:value-of select="name" />
                </zns:attribute>
                <zns:attribute>
                    <xsl:attribute name="name">mediarep</xsl:attribute>
                    <xsl:value-of select="mediarep" />
                </zns:attribute>
                <xsl:apply-templates select="attribute" />
            </zns:attributes>
            <zns:categories>
                <xsl:apply-templates select="categories/category" />
            </zns:categories>
        </zns:blog>
    </xsl:template>

    <!-- Matches the root element and begins the conversion to the new format. -->
    <xsl:template match="/blog-account">
        <zns:account>
            <xsl:attribute name="type">
                <xsl:value-of select="'weblog'"/>
            </xsl:attribute>
            <xsl:attribute name="account-id">
                <xsl:value-of select="id/text()"/>
            </xsl:attribute>
            <zns:attributes>
                <xsl:apply-templates select="name | type | username | password | icon"/>
            </zns:attributes>
            <zns:api-info>
                <zns:attributes>
                    <xsl:apply-templates select="api-info/*"/>
                </zns:attributes>
            </zns:api-info>
            <zns:blogs>
                <xsl:apply-templates select="blogs/blog" />
            </zns:blogs>
        </zns:account>
    </xsl:template>
    
</xsl:transform>
