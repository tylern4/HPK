// Copyright © 2023 FORTH-ICS
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package image

import (
	"strings"

	"github.com/carv-ics-forth/hpk/compute"
	"github.com/carv-ics-forth/hpk/pkg/process"
	"github.com/pkg/errors"
)

func Pull(imageDir string, transport Transport, imageName string) (*Image, error) {
	// Remove the digest form the image, because Singularity fails with
	// "Docker references with both a tag and digest are currently not supported".
	imageName = strings.Split(imageName, "@")[0]

	// NT notes:
	/*
	
	Podamn commmand images to see if the image is there based on the name, and also check if it is read only
	podman-hpc images --format="{{.Names}}|{{.Readonly}}" 
	this command needs 
	
	check if imageName is the same with the result and also if the readonly is true.
	if the check passes we don't have to pull but we can use directly 
	Keep in mind the ImagePullpolicy implementation for the future 

	*/

	res, err := process.Execute(compute.Environment.PodmanBin, "images", "--format={{.Names}}|{{.Readonly}}")
	if err != nil {
		return nil, errors.Wrapf(err, "Failed to check the image")
	}


	compute.DefaultLogger.Info(" The res from the images command is ", "res", res)

	// this string needs to be parsed deliminated by | and then check if the image is readonly
	// imageNameToCheck, readonly = strings.Split(res, "|")
	// // readonly = strings.Split(res, "|")[1]

	// if imageName == imageNameToCheck && readonly == "true" {
	// 	compute.DefaultLogger.Info(" * Image already exists", "image", imageName, "path", imageName)
	// 	return &Image{
	// 		ImageName: imageName,
	// 	}
	// }

	

	// otherwise, download a fresh copy
	if _, err := process.Execute(compute.Environment.PodmanBin, "pull", imageName); err != nil {
		return nil, errors.Wrapf(err, "downloading has failed")
	}


	img := &Image{
		ImageName: imageName,	
	}
	compute.DefaultLogger.Info(" * Download completed", "image", imageName, "path", img.ImageName)

	return img, nil
}

func ParseImageName(rawImageName string) string {
	// filter host
	var imageName string

	hostImage := strings.Split(rawImageName, "/")
	switch {
	case len(hostImage) == 1:
		imageName = hostImage[0]
	case len(hostImage) > 1:
		imageName = hostImage[len(hostImage)-1]
	default:
		panic("invalid name: " + rawImageName)
	}

	// filter version
	imageNameVersion := strings.Split(imageName, ":")
	switch {
	case len(imageNameVersion) == 1:
		name := imageNameVersion[0]
		version := "latest"

		return "/" + name + "_" + version + ".sif"
	case len(imageNameVersion) == 2:
		name := imageNameVersion[0]
		version := imageNameVersion[1]

		return "/" + name + "_" + version + ".sif"

	default:
		// keep the tag (version), but ignore the digest (sha256)
		// registry.k8s.io/ingress-nginx/kube-webhook-certgen:v20230407@sha256:543c40fd093964bc9ab509d3e791f9989963021f1e9e4c9c7b6700b02bfb227b
		imageNameVersionDigest := strings.Split(imageName, "@")
		digest := imageNameVersionDigest[1]
		_ = digest

		imageNameVersion = strings.Split(imageNameVersionDigest[0], ":")
		name := imageNameVersion[0]
		version := imageNameVersion[1]

		return "/" + name + "_" + version + ".sif"
	}
}
