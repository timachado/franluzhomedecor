package com.timachado.bibliaebd;

import android.webkit.PermissionRequest;

public final class LiveLensChromeClient extends LensChromeClient {
    public LiveLensChromeClient(LensActivity owner) {
        super(owner);
    }

    @Override
    public void onPermissionRequest(PermissionRequest request) {
        if (request == null) return;
        String[] resources = request.getResources();
        if (resources != null) {
            for (String resource : resources) {
                if (PermissionRequest.RESOURCE_VIDEO_CAPTURE.equals(resource)) {
                    request.grant(new String[]{ PermissionRequest.RESOURCE_VIDEO_CAPTURE });
                    return;
                }
            }
        }
        super.onPermissionRequest(request);
    }
}
