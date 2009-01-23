<xsl:transform xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='1.0'>

    <!-- 
        XSL Transform used to transform the manifest.xml file into
        HTML format for use in the About dialog box.
      -->

    <xsl:output method="html" />

    <!-- Matches a single <depends> element. -->
    <xsl:template match="depends">
        <li><font size="-1">
            <a>
                <xsl:attribute name="href">
                    <xsl:value-of select="homepage-url" />
                </xsl:attribute>
                <xsl:value-of select="name" />
            </a>
        </font></li>
    </xsl:template>

    <!-- Output the HTML document's HEAD. -->
    <xsl:template name="outputHead">
        <head>
            <title>Zoundry Raven Credits</title>
        </head>
    </xsl:template>

    <!-- Output the HTML document's BODY. -->
    <xsl:template name="outputBody">
        <body>
            <p><font size="-1">Zoundry Raven Logo, Graphics, Icon By:</font></p>
            <p>
               <blockquote>
                   <font size="-1">Jim Dustin Design</font><br/>
                   <font size="-1"><a href="http://www.jimdustindesign.com/">http://www.jimdustindesign.com</a></font>
               </blockquote>
            </p>
            <p><br/></p>

            <p><font size="-1">Various Icons used in Zoundry Raven By:</font></p>
		    <p>
		      <ul>
		      	<li><font size="-1">Mark James (FamFamFam)</font>
		      		<br/><font size="-1"><a href="http://www.famfamfam.com/">http://www.famfamfam.com/</a></font>
		      	</li>
		      	<li><font size="-1">dryicons.com</font>
		      		<br/><font size="-1"><a href="http://dryicons.com/">http://dryicons.com/</a></font>
		      	</li>
		      	
		      </ul>
		    </p>
            <p><font size="-1">Translations Contributed By:</font></p>
		    <p>
		      <ul>
		      	<li><font size="-1">Spanish</font>
		      		<br/><font size="-1">es_MX: Fëaluin <a href="http://profundamenteazul.blogspot.com/">http://profundamenteazul.blogspot.com</a></font>
		      	</li>
		      	<li><font size="-1">Chinese</font>
          			<br/><font size="-1">zh_CN: Mao Men <a href="http://www.maomen.net/">http://www.maomen.net/</a>
           			<br/> and Seacen (YoTu) <a href="http://www.yotu.org.cn">http://www.yotu.org.cn</a></font>		      	
		      	</li>		      	
                <li><font size="-1">Singhalese</font>
                    <br/><font size="-1">si_LK: G.S.N. Supun Budhajeewa <a href="mailto:budhajeewa@gmail.com">budhajeewa@gmail.com</a></font>
                </li>               
		      </ul>
		    </p>		    
            <p><font size="-1">The following technologies were used in the creation of 
            <b><i>Zoundry Raven</i></b>.</font></p>
            <p>
                <ul>
                <xsl:apply-templates
                    select="/zoundry-project/dependencies/dependency-set[not(@type = 'zoundry')]/depends" />
                </ul>
            </p>
        </body>
    </xsl:template>

    <!-- public static void main() -->
    <xsl:template match="/">
        <html>
            <xsl:call-template name="outputHead" />
            <xsl:call-template name="outputBody" />
        </html>
    </xsl:template>

</xsl:transform>
