function b64toBlob(b64Data, contentType, sliceSize) {
    contentType = contentType || '';
    sliceSize = sliceSize || 512;

    var byteCharacters = atob(b64Data);
    var byteArrays = [];

    for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        var slice = byteCharacters.slice(offset, offset + sliceSize);

        var byteNumbers = new Array(slice.length);
        for (var i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }
        var byteArray = new Uint8Array(byteNumbers);
        byteArrays.push(byteArray);
    }

    var blob = new Blob(byteArrays, {type: contentType});
    return blob;
}

function downloadPDF(tB, tF){
    if(window.top.navigator.msSaveOrOpenBlob){
        //Store Blob in IE
        window.top.navigator.msSaveOrOpenBlob(tB, tF)
    }
    else{
        //Store Blob in others
        var tA = document.body.appendChild(document.createElement('a'));
        tA.href = URL.createObjectURL(tB);
        tA.download = tF;
        tA.style.display = 'none';
        tA.click();
        tA.parentNode.removeChild(tA)
    }
}


function descargarPDFSeccion(seccion, fechaYMD, url_pdf, link_pdf_del_dia){
    link_pdf_del_dia = setDefault(link_pdf_del_dia, "");

    fechaHoy = new Date();
    fechaHoy = formatDateToYMD(fechaHoy);
    if (fechaYMD === fechaHoy && link_pdf_del_dia !== ""){
        window.open(link_pdf_del_dia,'_blank');
    }
    else{
        $("#loader").show();
        $.ajax({
            url: url_pdf,
            dataType : "json",
            type : "POST",
            data : {
                nombreSeccion : seccion,
            },
            error: function(xhr, ajaxOptions, thrownError){
                showFlashWarning("El pdf no pudo ser encontrado.");
                $("html, body").animate({scrollTop: 0}, 1000);
                $("#loader").hide();
            },
            success: function(data) {
                if (data == undefined || data == null || data['pdfBase64'] == undefined || data['pdfBase64'] == null){
                    showFlashWarning("El pdf no pudo ser encontrado.");
                    $("#loader").hide();
                    return;
                }
                var tB = b64toBlob(data['pdfBase64'], 'application/pdf');
                var tF = 'seccion_'+seccion+'_'+fechaYMD+'.pdf';

                downloadPDF(tB, tF);

                $("#loader").hide();
            }
        });
    }


}

function descargarPDFAviso(seccion, idAviso ,fechaPublicacion, url_pdf){
    $("#loader").show();
    $.ajax({
        url: url_pdf,
        dataType : "json",
        type : "POST",
        data : {
            nombreSeccion : seccion,
            idAviso : idAviso,
            fechaPublicacion: fechaPublicacion
        },
        error: function(a,b,c){
            showFlashWarning("El pdf no pudo ser encontrado.");
            $("#loader").hide();
        },
        success: function(data) {
            if (data == undefined || data == null || data['pdfBase64'] == undefined || data['pdfBase64'] == null){
                showFlashWarning("El pdf no pudo ser encontrado.");
                $("#loader").hide();
                return;
            }
            var tB = b64toBlob(data['pdfBase64'], 'application/pdf');
            var tF = 'aviso_'+idAviso+'.pdf';

            downloadPDF(tB, tF);

            $("#loader").hide();
        }
    });
}


function renderPDFAviso(url_pdf_aviso){
    $("#loader").show();
    file_name = encodeURIComponent(url_pdf_aviso);
    url = "/web/utils/pdfView?file=" + file_name;
    window.open(url,"_blank");
    $("#loader").hide();
}


function descargarPDFAnexo(seccion, nroAnexo, idAnexo ,fechaPublicacion, url_pdf){
    $("#loader").show();
    $.ajax({
        url: url_pdf,
        dataType : "json",
        type : "POST",
        data : {
            seccion: seccion,
            nroAnexo : nroAnexo,
            idAnexo : idAnexo,
            fechaPublicacion: fechaPublicacion
        },
        error: function(a,b,c){
            showFlashWarning("El pdf no pudo ser encontrado.");
            $("#loader").hide();
        },
        success: function(data) {
            if (data == undefined || data == null || data['pdfBase64'] == undefined || data['pdfBase64'] == null){
                showFlashWarning("El pdf no pudo ser encontrado.");
                backToTop();
                $("#loader").hide();
                return;
            }
            var tB = b64toBlob(data['pdfBase64'], 'application/pdf');
            var tF = 'anexo_'+idAnexo+'_'+nroAnexo+'.pdf';

            downloadPDF(tB, tF);

            $("#loader").hide();
        }
    });
}


function mostrarPdfSeccionPorPaginas(seccion, fecha, paginaDesde, paginaHasta, urlPdf, classPdf, classAviso){
    pdfCargado = $(classPdf).find("iframe")[0].src;
    if (pdfCargado === ""){
        $("#loader").show();
        $.ajax({
            url: urlPdf,
            dataType : "json",
            type : "POST",
            data : {
                nombreSeccion : seccion,
                fechaPublicacion: fecha,
                paginaDesde: paginaDesde,
                paginaHasta: paginaHasta
            },
            error: function(xhr, ajaxOptions, thrownError){
                showFlashWarning("No se encontro el pdf");
                $("html, body").animate({scrollTop: 0}, 1000);
                $("#loader").hide();
            },
            success: function(data) {
                if (data == undefined || data == null || data['pdfBase64'] == undefined || data['pdfBase64'] == null){
                    showFlashWarning("El pdf no pudo ser encontrado.");
                    $("#loader").hide();
                    return;
                }
                $(classAviso).hide();
                $(classPdf).show();
                pdf_url = convertBase64InUrlBlob(data["pdfBase64"]);
                $(classPdf).find("iframe")[0].src = "/web/utils/pdfView?file="+encodeURIComponent(pdf_url);
                $("#loader").hide();
                $(".pdf-aviso-printer").hide();
            }
        });
    }
    else{
        $(classAviso).hide();
        $(classPdf).show();
        $(".pdf-aviso-printer").hide();
    }

}


function convertBase64InUrlBlob(base64){
    var decodedPdfContent = atob(base64);
    var byteArray = new Uint8Array(decodedPdfContent.length);
    for(var i=0; i<decodedPdfContent.length; i++){
        byteArray[i] = decodedPdfContent.charCodeAt(i);
    }
    var blob = new Blob([byteArray.buffer], { type: 'application/pdf' });
    var _pdfurl = URL.createObjectURL(blob);
    return _pdfurl;
}