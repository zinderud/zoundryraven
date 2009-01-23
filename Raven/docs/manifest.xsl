<xsl:transform xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='1.0'>

   <xsl:output method="html" />

   <!-- Matches a single <depends> element. -->
   <xsl:template match="depends">
      <li> <a> <xsl:attribute name="href"> <xsl:value-of select="homepage-url" /> </xsl:attribute> 
         <xsl:value-of select="name" /> </a> (<b><font size="-1"><a><xsl:attribute name="href"> 
         <xsl:value-of select="download-url" /> </xsl:attribute>Download</a></font></b>) </li>
   </xsl:template>
   
   <!-- Matches a single <dependency-set> element. -->
   <xsl:template match="dependency-set">
         <h3>
            <xsl:value-of select="@description" />
         </h3>
         <ul>
            <!-- Now iterate through all the dependencies and put them in the ul. -->
            <xsl:apply-templates select="depends" />
         </ul>
   </xsl:template>

   <!-- Output the HTML document's HEAD. -->
   <xsl:template name="outputHead">
      <head>
         <title>
            <xsl:value-of select="/zoundry-project/title" />
         </title>
      </head>
   </xsl:template>

   <!-- Output the HTML document's BODY. -->
   <xsl:template name="outputBody">
      <body>
         <center>
            <h2><xsl:value-of select="/zoundry-project/title" /></h2>
            <table width="70%" border="1" cellpadding="10" cellspacing="0" bgcolor="#EEEEFF">
               <tr>
                  <td align="center">
                     <font size="+1">
                        <xsl:value-of select="/zoundry-project/description" />
                     </font>
                  </td>
               </tr>
            </table>
         </center>
         <br />
         <xsl:apply-templates select="/zoundry-project/dependencies/dependency-set" />
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
